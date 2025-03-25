"""
Services package for the CV Analysis Tool.
Contains modules for API communication, OpenAI integration, and text extraction.
"""

# Import all service modules for easy access
from app.services.api_client import APIClient
from app.services.text_extraction import extract_text_from_file, extract_text_from_pdf, extract_text_from_docx
from app.services.openai_client import summarize_cv_analyses, generate_interview_questions