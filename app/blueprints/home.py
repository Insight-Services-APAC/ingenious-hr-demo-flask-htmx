# File: app/blueprints/home.py
"""
Home page routes for the CV Analysis Tool Flask application.
"""

from flask import (
    Blueprint, flash, redirect, render_template, request, 
    url_for, current_app, session
)

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Home page with file upload and job criteria configuration."""
    # Clear results if requested
    if request.args.get('clear') == 'true':
        session.pop('results_id', None)
        session.pop('summary_content', None)
        session.pop('summary_generated', None)
        session.pop('interview_questions', None)
        return redirect(url_for('home.index'))
    
    return render_template('home.html')
