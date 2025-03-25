# File: app/__init__.py
"""
Flask application factory for CV Analysis Tool
"""

import os
from flask import Flask, session
from markupsafe import Markup
from datetime import datetime, timedelta
import markdown
from flask_session import Session

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Load configuration from app/config.py
    from app.config import Config
    app.config.from_object(Config)
    
    # Set up server-side session management
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-cv-analysis')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'flask_session')
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # Ensure session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize Flask-Session
    Session(app)
    
    # Configure file upload settings
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    from app.db import init_db, close_db
    with app.app_context():
        init_db()
    
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db(exception)
    
    # Register blueprints
    from app.blueprints import register_blueprints
    register_blueprints(app)
    
    # Set the default route
    app.add_url_rule('/', endpoint='home.index')
    
    # Add context processor for template variables
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Add custom filter for markdown rendering
    @app.template_filter('markdown')
    def render_markdown(text):
        if not text:
            return ""
        # Convert markdown to HTML and mark as safe
        return Markup(markdown.markdown(text, extensions=['tables', 'fenced_code']))
    
    return app
