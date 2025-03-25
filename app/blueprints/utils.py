# File: app/blueprints/utils.py
"""
Shared utility functions for blueprint routes.
"""

from flask import current_app, session
from app.db import store_analysis_results as db_store_results, get_results as db_get_results, clean_old_jobs as db_clean_old_jobs, create_job, update_job, get_job

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def store_analysis_results(results_id, results_data):
    """Store analysis results using SQLite."""
    return db_store_results(results_id, results_data)

def load_analysis_results(results_id):
    """Load analysis results using SQLite."""
    return db_get_results(results_id)

def get_results():
    """Helper to get analysis results from session ID."""
    if 'results_id' not in session:
        return None
    return load_analysis_results(session['results_id'])

def clean_old_jobs():
    """Clean old jobs from the DB."""
    db_clean_old_jobs()

# The in-memory analysis_jobs dictionary has been removed.
