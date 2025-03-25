# File: app/db.py
import sqlite3
import json
import time
from flask import current_app, g

DATABASE = 'app.db'  # Database file stored in the instance folder

def get_db():
    if 'db' not in g:
        db_path = current_app.instance_path + '/' + DATABASE
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Create table for analysis results
    db.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id TEXT PRIMARY KEY,
            results_data TEXT NOT NULL,
            created_at REAL,
            updated_at REAL
        )
    """)
    # Create table for analysis jobs (queue)
    db.execute("""
        CREATE TABLE IF NOT EXISTS analysis_jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT,
            progress REAL,
            message TEXT,
            results_id TEXT,
            started_at REAL,
            completed_at REAL
        )
    """)
    db.commit()

def store_analysis_results(results_id, results_data):
    db = get_db()
    now = time.time()
    results_json = json.dumps(results_data)
    db.execute(
        "INSERT OR REPLACE INTO analysis_results (id, results_data, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (results_id, results_json, now, now)
    )
    db.commit()
    return results_id

def load_analysis_results(results_id):
    db = get_db()
    row = db.execute("SELECT results_data FROM analysis_results WHERE id = ?", (results_id,)).fetchone()
    if row:
        return json.loads(row["results_data"])
    return None

def get_results(results_id):
    if not results_id:
        return None
    return load_analysis_results(results_id)

# Job queue helper functions
def create_job(job_id, job_data):
    db = get_db()
    db.execute(
        "INSERT INTO analysis_jobs (job_id, status, progress, message, results_id, started_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            job_id,
            job_data.get('status'),
            job_data.get('progress'),
            job_data.get('message'),
            job_data.get('results_id'),
            job_data.get('started_at'),
        )
    )
    db.commit()

def update_job(job_id, job_data):
    db = get_db()
    fields = []
    values = []
    for key in ['status', 'progress', 'message', 'results_id', 'completed_at']:
        if key in job_data:
            fields.append(f"{key} = ?")
            values.append(job_data[key])
    values.append(job_id)
    db.execute(f"UPDATE analysis_jobs SET {', '.join(fields)} WHERE job_id = ?", values)
    db.commit()

def get_job(job_id):
    db = get_db()
    row = db.execute("SELECT * FROM analysis_jobs WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None

def clean_old_jobs():
    db = get_db()
    current_time = time.time()
    # Delete jobs completed over 5 minutes ago or started more than 30 minutes ago
    db.execute("DELETE FROM analysis_jobs WHERE (completed_at IS NOT NULL AND (? - completed_at) > 300) OR (? - started_at) > 1800", (current_time, current_time))
    db.commit()
