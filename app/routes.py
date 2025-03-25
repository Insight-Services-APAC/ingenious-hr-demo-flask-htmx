"""
Route handlers for the CV Analysis Tool Flask application.
"""

import os
import json
import uuid
import pandas as pd
import time
import threading
import logging
import pickle
from flask import (
    Blueprint, flash, redirect, render_template, request, 
    url_for, current_app, session, jsonify, send_file
)
from werkzeug.utils import secure_filename
import tempfile
from io import StringIO

from app.services.api_client import APIClient
from app.services.text_extraction import extract_text_from_file
from app.services.openai_client import summarize_cv_analyses, generate_interview_questions
from app.utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure

bp = Blueprint('cv', __name__)

# Store analysis jobs in memory (in a production app, this would use Redis or a database)
analysis_jobs = {}

# Directory for storing analysis results
def get_results_dir():
    """Get the directory for storing analysis results."""
    results_dir = os.path.join(current_app.instance_path, 'analysis_results')
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def store_analysis_results(results_id, results_data):
    """Store analysis results to disk."""
    results_file = os.path.join(get_results_dir(), f"{results_id}.pkl")
    with open(results_file, 'wb') as f:
        pickle.dump(results_data, f)
    return results_id

def load_analysis_results(results_id):
    """Load analysis results from disk."""
    results_file = os.path.join(get_results_dir(), f"{results_id}.pkl")
    if os.path.exists(results_file):
        with open(results_file, 'rb') as f:
            return pickle.load(f)
    return None

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/')
def index():
    """Home page with file upload and job criteria configuration."""
    # Clear results if requested
    if request.args.get('clear') == 'true':
        if 'results_id' in session:
            try:
                # Remove the results file
                results_file = os.path.join(get_results_dir(), f"{session['results_id']}.pkl")
                if os.path.exists(results_file):
                    os.remove(results_file)
            except Exception as e:
                current_app.logger.error(f"Error removing results file: {str(e)}")
            
            # Clear session data
            session.pop('results_id', None)
            session.pop('summary_content', None)
            session.pop('summary_generated', None)
            session.pop('interview_questions', None)
        
        return redirect(url_for('cv.index'))
    
    return render_template('home.html')

@bp.route('/upload-cv', methods=['POST'])
def upload_cv():
    """Handle CV file uploads and process them."""
    if 'cv_files' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('cv.index'))
    
    files = request.files.getlist('cv_files')
    
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('cv.index'))
    
    # Create a job ID
    job_id = str(uuid.uuid4())
    
    # Save files temporarily
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append((filename, filepath))
    
    # Initialize job status
    analysis_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Starting analysis...',
        'results_id': None,
        'started_at': time.time()
    }
    
    # Start processing in a background thread
    # Create a copy of the current application for the thread
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=process_files_with_progress,
        args=(app, job_id, saved_files)
    )
    thread.daemon = True  # Make thread a daemon so it exits when the main process exits
    thread.start()
    
    # Return job ID for progress tracking
    return jsonify({
        'job_id': job_id,
        'status': 'processing'
    }), 202

def process_files_with_progress(app, job_id, saved_files):
    """Process files with progress tracking within app context."""
    # Create a logger that doesn't depend on Flask's app context
    logger = logging.getLogger(__name__)
    
    # Use the application context
    with app.app_context():
        try:
            job = analysis_jobs[job_id]
            job['status'] = 'processing'
            job['message'] = 'Starting analysis...'
            
            # Process each file
            total_files = len(saved_files)
            results = []
            
            for i, (filename, filepath) in enumerate(saved_files):
                try:
                    # Update progress (10-90% is for processing)
                    progress_percent = i / total_files
                    job['progress'] = 0.1 + (progress_percent * 0.8)
                    job['message'] = f'Analyzing {filename} ({i+1} of {total_files})...'
                    
                    # Extract text from file
                    cv_text = extract_text_from_file(filepath)
                    
                    # Send to API
                    identifier = f"cv_{len(results)+1}"
                    response = APIClient.create_chat(cv_text, identifier=identifier)
                    
                    # Store result
                    result = {
                        "CV Name": filename,
                        "Analysis": response.get("agent_response", "Analysis failed"),
                        "Thread ID": response.get("thread_id", ""),
                        "Message ID": response.get("message_id", "")
                    }
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f'Error processing {filename}: {str(e)}')
                    # Store error result
                    results.append({
                        "CV Name": filename,
                        "Analysis": f"Error: {str(e)}",
                        "Thread ID": "",
                        "Message ID": ""
                    })
                finally:
                    # Clean up temporary file
                    try:
                        os.remove(filepath)
                    except:
                        pass
            
            # Generate summary (last 10% of progress)
            job['progress'] = 0.9
            job['message'] = 'Generating summary...'
            
            # Generate summary automatically if we have results
            summary = None
            if results and app.config['AZURE_OPENAI_KEY'] and app.config['AZURE_OPENAI_ENDPOINT']:
                try:
                    summary = summarize_cv_analyses(results)
                except Exception as e:
                    logger.error(f'Error generating summary: {str(e)}')
                    summary = f"Error generating summary: {str(e)}"
            
            # Store results on disk
            results_data = {
                'results': results,
                'thread_ids': [r.get("Thread ID", "") for r in results],
                'summary': summary,
                'created_at': time.time()
            }
            
            results_id = store_analysis_results(job_id, results_data)
            
            # Mark job as completed
            job['status'] = 'completed'
            job['progress'] = 1.0
            job['message'] = 'Analysis complete'
            job['results_id'] = results_id
            job['completed_at'] = time.time()
            
        except Exception as e:
            logger.error(f'Error in process_files_with_progress: {str(e)}')
            job = analysis_jobs.get(job_id)
            if job:
                job['status'] = 'failed'
                job['message'] = str(e)
                
        finally:
            # Ensure all temporary files are cleaned up
            for _, filepath in saved_files:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass

@bp.route('/check-progress')
def check_progress():
    """Check the progress of an analysis job."""
    job_id = request.args.get('job_id')
    
    if not job_id or job_id not in analysis_jobs:
        return jsonify({
            'status': 'not_found',
            'message': 'Job not found'
        }), 404
    
    job = analysis_jobs[job_id]
    
    # If job is completed, store results ID in session
    if job['status'] == 'completed' and job.get('results_id') and not session.get('results_id'):
        session['results_id'] = job['results_id']
        
        # Clean up old jobs (keep for 5 minutes)
        clean_old_jobs()
    
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message']
    })

def clean_old_jobs():
    """Clean up old analysis jobs."""
    current_time = time.time()
    to_delete = []
    
    for job_id, job in analysis_jobs.items():
        if job.get('completed_at') and (current_time - job['completed_at']) > 300:  # 5 minutes
            to_delete.append(job_id)
        elif job.get('started_at') and (current_time - job['started_at']) > 1800:  # 30 minutes
            to_delete.append(job_id)
    
    for job_id in to_delete:
        analysis_jobs.pop(job_id, None)

def get_results():
    """Helper to get analysis results."""
    if 'results_id' not in session:
        return None
        
    results_data = load_analysis_results(session['results_id'])
    return results_data

@bp.route('/analysis')
def analysis():
    """Display analysis results for all CVs."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('cv.index'))
    
    return render_template('analysis.html', results=results_data['results'])

@bp.route('/cv/<int:index>')
def view_cv(index):
    """View individual CV analysis."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data or index >= len(results_data['results']):
        flash('CV analysis not found', 'error')
        return redirect(url_for('cv.analysis'))
    
    result = results_data['results'][index]
    return render_template('components/cv_analysis.html', result=result, index=index)

@bp.route('/summary')
def summary():
    """Display comparative summary of all CVs."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('cv.index'))
    
    # Store summary in session for rendering (smaller than the full results)
    if 'summary' in results_data and not session.get('summary_content'):
        session['summary_content'] = results_data['summary']
        session['summary_generated'] = True
    
    return render_template('summary.html')

@bp.route('/regenerate-summary', methods=['POST'])
def regenerate_summary():
    """Regenerate the comparative summary."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        return jsonify({'error': 'No results available'}), 400
    
    try:
        summary = summarize_cv_analyses(results_data['results'])
        
        # Update both session and stored results
        session['summary_content'] = summary
        session['summary_generated'] = True
        
        # Update the saved results
        results_data['summary'] = summary
        store_analysis_results(session['results_id'], results_data)
        
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/interview')
def interview():
    """Display interview questions generator."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('cv.index'))
    
    # Initialize interview questions in session if not exists
    if 'interview_questions' not in session:
        session['interview_questions'] = {}
    
    cv_options = [result["CV Name"] for result in results_data['results']]
    selected_cv = request.args.get('cv')
    
    # If no CV selected, use the first one
    if not selected_cv and cv_options:
        selected_cv = cv_options[0]
    
    return render_template('interview.html', 
                          cv_options=cv_options, 
                          selected_cv=selected_cv,
                          questions=session.get('interview_questions', {}).get(selected_cv, None))

@bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Generate interview questions for a selected CV."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        return jsonify({'error': 'No results available'}), 400
    
    selected_cv = request.form.get('cv')
    if not selected_cv:
        return jsonify({'error': 'No CV selected'}), 400
    
    # Find the CV in results
    cv_index = None
    for i, result in enumerate(results_data['results']):
        if result['CV Name'] == selected_cv:
            cv_index = i
            break
    
    if cv_index is None:
        return jsonify({'error': 'Selected CV not found'}), 404
    
    try:
        questions = generate_interview_questions(results_data['results'][cv_index])
        
        # Store in session
        if 'interview_questions' not in session:
            session['interview_questions'] = {}
        
        session['interview_questions'][selected_cv] = questions
        
        return jsonify({
            'success': True, 
            'questions': questions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/download-questions/<cv_name>')
def download_questions(cv_name):
    """Download interview questions as a text file."""
    if 'interview_questions' not in session or cv_name not in session['interview_questions']:
        flash('No questions available for download', 'error')
        return redirect(url_for('cv.interview'))
    
    questions = session['interview_questions'][cv_name]
    
    # Create a temporary file
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(questions.encode('utf-8'))
    temp.close()
    
    return send_file(
        temp.name,
        as_attachment=True,
        download_name=f"interview_questions_{cv_name.replace(' ', '_')}.txt",
        mimetype="text/plain"
    )

@bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on an analysis."""
    message_id = request.form.get('message_id')
    thread_id = request.form.get('thread_id')
    positive = request.form.get('positive') == 'true'
    
    if not message_id or not thread_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        feedback = APIClient.submit_feedback(message_id, thread_id, positive)
        return jsonify({'success': True, 'response': feedback})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/upload-job-criteria', methods=['POST'])
def upload_job_criteria():
    """Handle job criteria file upload and update."""
    if 'job_criteria_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['job_criteria_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text from file
            job_text = extract_text_from_file(filepath)
            
            # Convert to JSON
            job_criteria = convert_text_to_job_criteria_json(job_text)
            
            # Return extracted text and JSON for preview
            return jsonify({
                'success': True,
                'extracted_text': job_text,
                'job_criteria': job_criteria
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary file
            os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/update-job-criteria', methods=['POST'])
def update_criteria():
    """Update job criteria in Azure Blob Storage."""
    job_criteria = request.json.get('job_criteria')
    
    if not job_criteria:
        return jsonify({'error': 'No job criteria provided'}), 400
    
    success = update_job_criteria_in_azure(job_criteria)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update job criteria'}), 500

@bp.route('/export-results')
def export_results():
    """Export analysis results as CSV."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No results available to export', 'error')
        return redirect(url_for('cv.analysis'))
    
    # Convert results to CSV
    df = pd.DataFrame(results_data['results'])
    csv_data = df.to_csv(index=False)
    
    # Create a temporary file
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(csv_data.encode('utf-8'))
    temp.close()
    
    return send_file(
        temp.name,
        as_attachment=True,
        download_name="cv_analysis_results.csv",
        mimetype="text/csv"
    )