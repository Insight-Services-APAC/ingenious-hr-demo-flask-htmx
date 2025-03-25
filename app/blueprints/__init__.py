"""
Blueprints package for CV Analysis Tool.
Makes all blueprints importable from app.blueprints
"""

from app.blueprints.home import bp as home_bp
from app.blueprints.analysis import bp as analysis_bp
from app.blueprints.cv_detail import bp as cv_detail_bp
from app.blueprints.interview import bp as interview_bp
from app.blueprints.summary import bp as summary_bp
from app.blueprints.feedback import bp as feedback_bp
from app.blueprints.job_criteria import bp as job_criteria_bp

def register_blueprints(app):
    """Register all blueprints with the app."""
    app.register_blueprint(home_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(cv_detail_bp, url_prefix='/cv')
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(summary_bp, url_prefix='/summary')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    app.register_blueprint(job_criteria_bp, url_prefix='/job-criteria')