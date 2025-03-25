# File: app/blueprints/analysis.py
"""
Analysis routes for the CV Analysis Tool Flask application.
"""

import os
import uuid
import time
import threading
import logging
import pandas as pd
import tempfile
from flask import (
    Blueprint, flash, redirect, render_template, request, 
    url_for, current_app, session, jsonify, send_file
)
from werkzeug.utils import secure_filename

from app.services.api_client import APIClient
from app.services.text_extraction import extract_text_from_file
from app.services.openai_client import summarize_cv_analyses
from app.blueprints.utils import allowed_file, store_analysis_results, get_results
from app.db import create_job, update_job, get_job, clean_old_jobs

bp = Blueprint('analysis', __name__)

@bp.route('/')
def index():
    """Display analysis results for all CVs."""
    results_data = get_results()
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('home.index'))
    return render_template('analysis.html', results=results_data['results'])

@bp.route('/upload-cv', methods=['POST'])
def upload_cv():
    """Handle CV file uploads and process them."""
    if 'cv_files' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home.index'))
    
    files = request.files.getlist('cv_files')
    if not files or files[0].filename == '':
        flash('No files selected', 'error')
        return redirect(url_for('home.index'))
    
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
    
    # Initialize job status in the database
    job_data = {
        'status': 'processing',
        'progress': 0,
        'message': 'Starting analysis...',
        'results_id': None,
        'started_at': time.time()
    }
    create_job(job_id, job_data)
    
    # Start processing in a background thread
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=process_files_with_progress,
        args=(app, job_id, saved_files)
    )
    thread.daemon = True
    thread.start()
    
    # Return job ID for progress tracking via AJAX
    return jsonify({
        'job_id': job_id,
        'status': 'processing'
    }), 202

@bp.route('/check-progress')
def check_progress():
    """Check the progress of an analysis job."""
    job_id = request.args.get('job_id')
    job = get_job(job_id)
    if not job:
        return jsonify({'status': 'not_found', 'message': 'Job not found'}), 404
    
    # If job is completed, store results ID in session
    if job['status'] == 'completed' and job.get('results_id') and not session.get('results_id'):
        session['results_id'] = job['results_id']
        clean_old_jobs()
    
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message']
    })

@bp.route('/export')
def export_results():
    """Export analysis results as CSV."""
    results_data = get_results()
    if not results_data or 'results' not in results_data:
        flash('No results available to export', 'error')
        return redirect(url_for('analysis.index'))
    
    df = pd.DataFrame(results_data['results'])
    csv_data = df.to_csv(index=False)
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(csv_data.encode('utf-8'))
    temp.close()
    
    return send_file(
        temp.name,
        as_attachment=True,
        download_name="cv_analysis_results.csv",
        mimetype="text/csv"
    )

def process_files_with_progress(app, job_id, saved_files):
    """Process files with progress tracking within app context."""
    logger = logging.getLogger(__name__)
    with app.app_context():
        try:
            # Fetch the job from the database
            job = get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found in DB")
                return
            
            total_files = len(saved_files)
            results = []
            for i, (filename, filepath) in enumerate(saved_files):
                try:
                    progress_percent = i / total_files
                    update_job(job_id, {
                        'progress': 0.1 + (progress_percent * 0.8),
                        'message': f'Analyzing {filename} ({i+1} of {total_files})...'
                    })
                    
                    cv_text = extract_text_from_file(filepath)
                    identifier = f"cv_{len(results)+1}"
                    response = APIClient.create_chat(cv_text, identifier=identifier)
                    
                    results.append({
                        "CV Name": filename,
                        "Analysis": response.get("agent_response", "Analysis failed"),
                        "Thread ID": response.get("thread_id", ""),
                        "Message ID": response.get("message_id", "")
                    })
                except Exception as e:
                    logger.error(f'Error processing {filename}: {str(e)}')
                    results.append({
                        "CV Name": filename,
                        "Analysis": f"Error: {str(e)}",
                        "Thread ID": "",
                        "Message ID": ""
                    })
                finally:
                    try:
                        os.remove(filepath)
                    except:
                        pass
            
            update_job(job_id, {'progress': 0.9, 'message': 'Generating summary...'})
            
            summary = None
            if results and app.config['AZURE_OPENAI_KEY'] and app.config['AZURE_OPENAI_ENDPOINT']:
                try:
                    summary = summarize_cv_analyses(results)
                except Exception as e:
                    logger.error(f'Error generating summary: {str(e)}')
                    summary = f"Error generating summary: {str(e)}"
            
            results_data = {
                'results': results,
                'thread_ids': [r.get("Thread ID", "") for r in results],
                'summary': summary,
                'created_at': time.time()
            }
            
            store_analysis_results(job_id, results_data)
            
            update_job(job_id, {
                'status': 'completed',
                'progress': 1.0,
                'message': 'Analysis complete',
                'results_id': job_id,
                'completed_at': time.time()
            })
            
        except Exception as e:
            logger.error(f'Error in process_files_with_progress: {str(e)}')
            job = get_job(job_id)
            if job:
                update_job(job_id, {
                    'status': 'failed',
                    'message': str(e)
                })
        finally:
            for _, filepath in saved_files:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass
