"""
Functions for extracting text from various document types.
"""

import os
from io import BytesIO
import docx2txt
import pypdf


def extract_text_from_file(file_path: str) -> str:
    """Extract text content from various file types."""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            return extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            return extract_text_from_docx(file_path)
        elif file_extension in [".txt", ".md", ".json"]:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Unsupported file type: {file_extension}"
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    with open(file_path, 'rb') as f:
        pdf_reader = pypdf.PdfReader(f)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()

    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    return docx2txt.process(file_path)