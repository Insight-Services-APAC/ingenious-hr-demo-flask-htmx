"""
API client for interacting with the FastAgent API.
Handles authentication, CV submission, and feedback submission.
"""

import requests
import json
import uuid
from typing import Dict, Any, Optional
from flask import current_app

class APIClient:
    """Client for interacting with the FastAgent API."""

    @classmethod
    def create_chat(cls, cv_content: str, thread_id: Optional[str] = None, identifier: Optional[str] = None) -> Dict[str, Any]:
        """Send a CV for analysis and get the results."""
        url = f"{current_app.config['API_BASE_URL']}/chat"

        # Format the CV content as required by the API
        user_prompt_data = {
            "revision_id": current_app.config['DEFAULT_REVISION_ID'],
            "identifier": identifier or str(uuid.uuid4())[:8],
            "Page_1": cv_content
        }

        # Convert the user_prompt_data to a JSON string
        user_prompt_json = json.dumps(user_prompt_data)

        payload = {
            "thread_id": thread_id or str(uuid.uuid4()),
            "conversation_flow": "hr_insights",
            "user_prompt": user_prompt_json
        }

        try:
            # Use basic authentication from environment variables
            auth = (current_app.config['API_USERNAME'], current_app.config['API_PASSWORD'])
            response = requests.post(url, json=payload, auth=auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"API Error: {str(e)}")
            return {"error": str(e)}

    @classmethod
    def submit_feedback(cls, message_id: str, thread_id: str, positive: bool) -> Dict[str, Any]:
        """Submit feedback on an analysis."""
        url = f"{current_app.config['API_BASE_URL']}/messages/{message_id}/feedback"

        payload = {
            "thread_id": thread_id,
            "message_id": message_id,
            "user_id": "flask_user",
            "positive_feedback": positive
        }

        try:
            # Use basic authentication
            auth = (current_app.config['API_USERNAME'], current_app.config['API_PASSWORD'])
            response = requests.put(url, json=payload, auth=auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"API Error: {str(e)}")
            return {"error": str(e)}