"""
Feedback routes for the CV Analysis Tool Flask application.
"""

from flask import (
    Blueprint, flash, redirect, request, url_for
)

from app.services.api_client import APIClient

bp = Blueprint('feedback', __name__)

@bp.route('/submit', methods=['POST'])
def submit():
    """Submit feedback on an analysis."""
    message_id = request.form.get('message_id')
    thread_id = request.form.get('thread_id')
    positive = request.form.get('positive') == 'true'
    
    if not message_id or not thread_id:
        flash('Missing required parameters', 'error')
        return redirect(url_for('analysis.index'))
    
    try:
        feedback = APIClient.submit_feedback(message_id, thread_id, positive)
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        flash(f'Error submitting feedback: {str(e)}', 'error')
    
    # Redirect back to the proper page - try to get the CV index from request
    cv_index = request.form.get('cv_index')
    if cv_index is not None:
        try:
            cv_index = int(cv_index)
            return redirect(url_for('cv_detail.view', index=cv_index))
        except:
            pass
    
    return redirect(url_for('analysis.index'))