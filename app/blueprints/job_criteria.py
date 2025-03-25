"""
Job criteria routes for the CV Analysis Tool Flask application.
"""

import os
from flask import (
    Blueprint, flash, redirect, render_template, request, 
    url_for, current_app, session, jsonify
)
from werkzeug.utils import secure_filename

from app.services.text_extraction import extract_text_from_file
from app.utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure
from app.blueprints.utils import allowed_file

bp = Blueprint('job_criteria', __name__)

@bp.route('/upload', methods=['POST'])
def upload():
    """Handle job criteria file upload and update."""
    if 'job_criteria_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home.index'))
    
    file = request.files['job_criteria_file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('home.index'))
    
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
            
            # Store in session for the confirmation page
            session['job_criteria_preview'] = {
                'extracted_text': job_text,
                'job_criteria': job_criteria
            }
            
            return redirect(url_for('job_criteria.preview'))
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        finally:
            # Clean up temporary file
            try:
                os.remove(filepath)
            except:
                pass
    else:
        flash('Invalid file type', 'error')
    
    return redirect(url_for('home.index'))

@bp.route('/preview')
def preview():
    """Display preview of extracted job criteria before updating."""
    if 'job_criteria_preview' not in session:
        flash('No job criteria data available', 'error')
        return redirect(url_for('home.index'))
    
    preview_data = session['job_criteria_preview']
    return render_template('job_criteria_preview.html', 
                          extracted_text=preview_data['extracted_text'],
                          job_criteria=preview_data['job_criteria'])

@bp.route('/update', methods=['POST'])
def update():
    """Update job criteria in Azure Blob Storage."""
    # For traditional form submission
    if request.is_json:
        job_criteria = request.json.get('job_criteria')
    else:
        # If form-encoded, try to get from session
        if 'job_criteria_preview' not in session:
            flash('No job criteria data available', 'error')
            return redirect(url_for('home.index'))
        job_criteria = session['job_criteria_preview']['job_criteria']
    
    if not job_criteria:
        flash('No job criteria provided', 'error')
        return redirect(url_for('home.index'))
    
    # For AJAX requests
    if request.is_json:
        success = update_job_criteria_in_azure(job_criteria)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to update job criteria'}), 500
    
    # For traditional form submission
    success = update_job_criteria_in_azure(job_criteria)
    
    if success:
        flash('Job criteria updated successfully', 'success')
    else:
        flash('Failed to update job criteria', 'error')
    
    return redirect(url_for('home.index'))