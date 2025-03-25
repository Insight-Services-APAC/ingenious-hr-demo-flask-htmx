"""
Configuration settings for CV Analysis Tool Flask application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Flask app."""
    
    # API Configuration
    API_BASE_URL = os.getenv(
        "API_BASE_URL", "https://hr-demo-app.ambitiousriver-e696f55c.australiaeast.azurecontainerapps.io/api/v1")
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")
    DEFAULT_REVISION_ID = os.getenv(
        "REVISION_ID", "5ccc4a42-1e24-4b82-a550-e7e9c6ffa48b")

    # Azure Blob Storage Configuration
    AZURE_BLOB_STORAGE_URL = os.getenv("AZURE_BLOB_STORAGE_URL", "")

    # Azure OpenAI API Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    # Flask-specific configuration
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}