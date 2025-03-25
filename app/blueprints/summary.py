"""
Summary routes for the CV Analysis Tool Flask application.
"""

from flask import (
    Blueprint, flash, redirect, render_template, session, 
    url_for
)

from app.services.openai_client import summarize_cv_analyses
from app.blueprints.utils import get_results, store_analysis_results

bp = Blueprint('summary', __name__)

@bp.route('/')
def index():
    """Display comparative summary of all CVs."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No CV analysis results available', 'warning')
        return redirect(url_for('home.index'))
    
    # Store summary in session for rendering (smaller than the full results)
    if 'summary' in results_data and not session.get('summary_content'):
        session['summary_content'] = results_data['summary']
        session['summary_generated'] = True
    
    return render_template('summary.html')

@bp.route('/regenerate', methods=['POST'])
def regenerate():
    """Regenerate the comparative summary."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data:
        flash('No results available', 'error')
        return redirect(url_for('summary.index'))
    
    try:
        summary = summarize_cv_analyses(results_data['results'])
        
        # Update both session and stored results
        session['summary_content'] = summary
        session['summary_generated'] = True
        
        # Update the saved results
        results_data['summary'] = summary
        store_analysis_results(session['results_id'], results_data)
        
        flash('Summary regenerated successfully', 'success')
        return redirect(url_for('summary.index'))
    except Exception as e:
        flash(f'Error generating summary: {str(e)}', 'error')
        return redirect(url_for('summary.index'))