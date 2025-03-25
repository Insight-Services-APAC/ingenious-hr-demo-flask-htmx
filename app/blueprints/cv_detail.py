"""
CV detail routes for the CV Analysis Tool Flask application.
"""

from flask import (
    Blueprint, flash, redirect, render_template, 
    url_for
)

from app.blueprints.utils import get_results

bp = Blueprint('cv_detail', __name__)

@bp.route('/<int:index>')
def view(index):
    """View individual CV analysis."""
    results_data = get_results()
    
    if not results_data or 'results' not in results_data or index >= len(results_data['results']):
        flash('CV analysis not found', 'error')
        return redirect(url_for('analysis.index'))
    
    result = results_data['results'][index]
    return render_template('cv_detail.html', result=result, index=index)