"""
Interview questions routes for the CV Analysis Tool Flask application.
"""

import tempfile
from flask import (
    Blueprint, flash, redirect, render_template, request, 
    url_for, session, send_file
)

from app.services.openai_client import generate_interview_questions
from app.blueprints.utils import get_results

bp = Blueprint('interview', __name__)

@bp.route('/')
def index():
    """Display interview questions generator."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('home.index'))
    
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

@bp.route('/generate', methods=['POST'])
def generate_questions():
    """Generate interview questions for a selected CV."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No results available', 'error')
        return redirect(url_for('interview.index'))
    
    selected_cv = request.form.get('cv')
    if not selected_cv:
        flash('No CV selected', 'error')
        return redirect(url_for('interview.index'))
    
    # Find the CV in results
    cv_index = None
    for i, result in enumerate(results_data['results']):
        if result['CV Name'] == selected_cv:
            cv_index = i
            break
    
    if cv_index is None:
        flash('Selected CV not found', 'error')
        return redirect(url_for('interview.index'))
    
    try:
        questions = generate_interview_questions(results_data['results'][cv_index])
        
        # Store in session
        if 'interview_questions' not in session:
            session['interview_questions'] = {}
        
        session['interview_questions'][selected_cv] = questions
        
        # Redirect back to interview page with the selected CV
        return redirect(url_for('interview.index', cv=selected_cv))
    except Exception as e:
        flash(f'Error generating questions: {str(e)}', 'error')
        return redirect(url_for('interview.index'))

@bp.route('/download/<cv_name>')
def download_questions(cv_name):
    """Download interview questions as a text file."""
    if 'interview_questions' not in session or cv_name not in session['interview_questions']:
        flash('No questions available for download', 'error')
        return redirect(url_for('interview.index'))
    
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