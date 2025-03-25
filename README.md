# CV Analysis Tool

## Overview

The CV Analysis Tool is a web-based application designed to assist recruiters in evaluating and comparing candidate CVs. Built with Flask and HTMX, the tool enables users to upload multiple CV files (PDF, DOCX, TXT), process them via an external API, and generate detailed analyses. Additionally, it leverages Azure OpenAI services to create comprehensive comparative summaries and tailored interview questions. With integrated job criteria configuration and export capabilities, the application streamlines the recruitment process from CV assessment to interview preparation.

## Features

- **CV File Upload & Analysis:** Upload one or more CVs for automated processing.
- **Real-Time Progress Tracking:** Monitor the status of file uploads and analysis via a dynamic progress bar.
- **Comparative Summary:** Generate detailed summaries comparing candidate qualifications, experience, and skills.
- **Interview Question Generation:** Create tailored interview questions based on the CV analyses.
- **Job Criteria Configuration:** Update evaluation criteria by uploading job description documents.
- **Feedback Mechanism:** Submit feedback on the quality of CV analyses.
- **Export Results:** Export analysis data as CSV for further review.

## Project Structure

```
flask-htmx-hr-demo/
├── app.py
├── requirements.txt
├── .env.example
└── app/
    ├── __init__.py
    ├── config.py
    ├── routes.py
    ├── services/
    │   ├── api_client.py
    │   ├── openai_client.py
    │   └── text_extraction.py
    ├── static/
    │   └── js/
    │       ├── home.js
    │       └── main.js
    ├── templates/
    │   ├── analysis.html
    │   ├── home.html
    │   ├── interview.html
    │   ├── summary.html
    │   ├── components/
    │   │   ├── cv_analysis.html
    │   │   ├── feedback.html
    │   │   ├── file_upload.html
    │   │   └── job_criteria.html
    │   └── layouts/
    │       └── base.html
    └── utils/
        └── helpers.py
```

## Key Files and Their Roles

- **app.py**  
  Entry point for the Flask application. It creates and runs the app using the application factory pattern.

- **requirements.txt**  
  Lists all Python dependencies required to run the application, ensuring reproducible environments.

- **.env.example**  
  A sample environment configuration file that includes settings for Flask, API credentials, Azure Blob Storage, and Azure OpenAI.

- **app/\_\_init\_\_.py**  
  Contains the Flask application factory (`create_app()`). It sets up sessions, file upload configurations, registers routes, and adds custom template filters.

- **app/config.py**  
  Loads configuration settings from environment variables (using dotenv) and sets default values for the application.

- **app/routes.py**  
  Defines the URL routes and view functions for handling file uploads, processing analyses, generating summaries and interview questions, managing feedback, and updating job criteria.

- **app/services/api_client.py**  
  Implements a client for interacting with an external API (FastAgent API) to submit CVs for analysis and to handle feedback submissions.

- **app/services/openai_client.py**  
  Handles integration with Azure OpenAI services to generate comprehensive summaries and tailored interview questions from CV analysis data.

- **app/services/text_extraction.py**  
  Provides functions to extract text content from various document types (PDF, DOCX, TXT).

- **app/utils/helpers.py**  
  Contains utility functions, such as converting extracted text into a JSON format for job criteria and updating job criteria in Azure Blob Storage.

- **Templates (app/templates/)**  
  Contains HTML templates that form the user interface, including layouts, views for home, analysis results, comparative summaries, and interview question generation.

- **Static JavaScript (app/static/js/)**  
  Includes client-side scripts to manage UI interactions, file uploads, progress tracking, and integration with HTMX and Bootstrap components.

## Setup and Running

1. **Clone the Repository:**  
   Clone the project repository to your local machine.

2. **Install Dependencies:**  
   Create a virtual environment and install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**  
   Copy `.env.example` to `.env` and update the configuration values (e.g., API credentials, Azure endpoints, and keys).

4. **Run the Application:**  
   Start the Flask application using:
   ```bash
   python app.py
   ```
   The application will run in development mode with debugging enabled.

5. **Access the Application:**  
   Open your web browser and navigate to [http://localhost:5000](http://localhost:5000) to start using the CV Analysis Tool.

## Summary

The CV Analysis Tool offers a comprehensive solution for recruiters to assess candidate profiles efficiently. By combining automated CV analysis, advanced AI-powered summaries, and tailored interview question generation, this tool simplifies the recruitment workflow and enhances decision-making.