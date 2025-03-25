"""
General utility functions for the CV Analysis Tool.
"""

import json
from typing import Dict, Any
from flask import current_app


def convert_text_to_job_criteria_json(text: str) -> Dict[str, Any]:
    """Convert extracted text from document to a simple job criteria JSON format.

    This just takes the extracted text and places it in one string value in the JSON,
    without attempting to parse specific fields.
    """
    # Simple conversion to a JSON object with a single text field
    criteria = {
        "job_criteria_text": text
    }

    return criteria


def update_job_criteria_in_azure(job_criteria: Dict[str, Any]) -> bool:
    """Update job criteria using direct Azure SDK calls with the full URL."""
    try:
        import os
        from azure.storage.blob import BlobClient

        # Get the full URL
        blob_url = current_app.config['AZURE_BLOB_STORAGE_URL']

        if not blob_url:
            current_app.logger.error("Azure Blob Storage URL not configured")
            return False

        current_app.logger.info(f"Connecting to blob at: {blob_url.split('?')[0]}")

        # Create a blob client
        blob_client = BlobClient.from_blob_url(blob_url)

        # Upload the content
        job_criteria_json = json.dumps(job_criteria, indent=2)
        blob_client.upload_blob(job_criteria_json, overwrite=True)

        current_app.logger.info("Job criteria updated successfully!")
        return True
    except Exception as e:
        current_app.logger.error(f"Error updating job criteria: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return False