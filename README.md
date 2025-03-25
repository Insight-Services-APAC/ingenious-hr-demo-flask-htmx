# CV Analysis Tool

## Overview

The **CV Analysis Tool** is a web-based application designed to streamline the recruitment process for HR teams and recruiters. It allows you to upload candidate CVs in various formats (PDF, DOCX, or TXT), extract and analyze the content with AI-powered services, and generate detailed insights and interview questions. The tool also provides a mechanism to update and preview job evaluation criteria based on uploaded job description documents, enabling a continuous and adaptive recruitment strategy.

### Key Features

- **CV Upload & Analysis:**  
  Upload multiple CVs at once, extract text content automatically, and receive AI-driven analyses of each document.

- **Comparative Summary:**  
  Generate a comprehensive, side-by-side summary highlighting the strengths and weaknesses of all analyzed CVs.

- **Interview Questions:**  
  Automatically produce tailored interview questions based on each candidate’s unique CV analysis.

- **Job Criteria Update:**  
  Dynamically update the job evaluation criteria by uploading a job description document. The system parses the document to create or refine the evaluation framework.

- **Feedback Mechanism:**  
  Submit feedback on the AI analysis to help refine future performance (via the integrated API feedback feature).

- **Export Results:**  
  Download all CV analysis results in a CSV file for archiving or offline review.

## Project Structure

Below is a high-level view of the project's structure:

```
flask-htmx-hr-demo/
├── app.py
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── blueprints/
│   ├── services/
│   ├── static/
│   ├── templates/
│   └── utils/
└── instance/
    ├── app.db
    ├── flask_session/
    └── uploads/
```

## Key Files and Their Roles

### Top-Level Files

- **Dockerfile**  
  Defines the container image setup for deploying the application. Installs Python dependencies, sets up environment variables, and starts the Flask application.

- **.dockerignore**  
  Specifies files and folders to ignore when building the Docker image (e.g., local `.env` files, caches, and instance data).

- **.env.example**  
  Provides an example of the environment variables needed (e.g., API credentials, Azure settings). Copy and rename this to `.env` and fill in the required values before running the application.

- **app.py**  
  The entry point for running the Flask application. It creates the Flask app instance by calling `create_app()` from `app/__init__.py`.

- **requirements.txt**  
  Lists all Python dependencies for the project. Installing from this file ensures all necessary libraries (e.g., Flask, Azure, PyPDF) are available.

### The `app/` Package

- **`app/__init__.py`**  
  Implements the Flask application factory (`create_app`). Configures environment settings, initializes the database, sets up session management, and registers blueprints.

- **`app/config.py`**  
  Loads configuration settings (including environment variables) such as API base URLs and allowed file extensions. Contains the central configuration class used across the application.

- **`app/db.py`**  
  Manages a local SQLite database used to track analysis results, job statuses, and job queues. Provides functions to initialize, retrieve, and store results in the database.

- **`app/blueprints/`**  
  Houses modular route handlers that separate core functionalities:
  - **home.py:** Manages the home page where users can upload CVs and job criteria files.
  - **analysis.py:** Handles processing and analysis of uploaded CV files. Manages background jobs, progress checking, and exporting results as CSV.
  - **cv_detail.py:** Displays the detailed analysis of a single CV.
  - **feedback.py:** Allows users to submit feedback on the AI analysis.
  - **interview.py:** Generates interview questions based on a selected CV analysis.
  - **job_criteria.py:** Handles the upload and preview of job description documents to update job evaluation criteria.
  - **summary.py:** Creates and displays a comparative summary of all analyzed CVs.

- **`app/services/`**  
  Contains modules for external service integrations:
  - **api_client.py:** Communicates with the FastAgent API to submit CV content, retrieve analysis results, and handle feedback submissions.
  - **openai_client.py:** Connects to Azure OpenAI to build prompts, summarize multiple analyses, and generate interview questions.
  - **text_extraction.py:** Provides functions to extract text from PDF, DOCX, and TXT files.

- **`app/static/`**  
  Contains static assets such as JavaScript files.  
  - **js/home.js:** Handles the user interactions on the home page (e.g., CV file uploads and their progress, job criteria form submissions).  
  - **js/main.js:** Initializes Bootstrap components like tooltips and popovers.

- **`app/templates/`**  
  Stores HTML templates for rendering pages.  
  - **layouts/base.html:** The main template that defines the layout shared by all pages.  
  - **analysis.html, cv_detail.html, home.html, interview.html, etc.:** Individual page templates for different sections/features in the application.  
  - **components/:** Houses smaller reusable HTML components (e.g., file upload, feedback sections).

- **`app/utils/`**  
  Contains utility functions:
  - **helpers.py:** Functions for converting text into a job-criteria JSON format and updating files in Azure Blob Storage.

### The `instance/` Folder

- **app.db:**  
  SQLite database file containing stored analysis results and job data.

- **flask_session/:**  
  Directory for server-side sessions (managed by Flask-Session).

- **uploads/:**  
  Temporary storage for uploaded files (CVs and job description documents) during analysis.

## Running the Application

1. **Set Up Environment Variables**  
   - Copy `.env.example` to `.env` and fill in your own credentials (API keys, Azure credentials, etc.).

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask Application**  
   ```bash
   python app.py
   ```
   By default, this starts the server at `http://localhost:5000`.

This setup allows you to analyze multiple CVs, review AI-generated insights, generate interview questions, and maintain dynamic job evaluation criteria—all from a single, user-friendly web interface.
