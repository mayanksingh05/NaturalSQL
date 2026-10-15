import os
import sys
import shutil
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import (
    save_uploaded_file,
    create_sqlite_database,
    extract_schema,
    execute_query,
    sanitize_session_id,
    UPLOAD_DIR
)
from sql_service import generate_sql

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3"}

class AskRequest(BaseModel):
    question: str
    api_key: str
    session_id: str
    schema_data: list

class ExecuteRequest(BaseModel):
    query: str
    session_id: str

def cleanup_old_sessions():
    """Deletes session folders older than 2 hours to free up storage."""
    try:
        if not os.path.exists(UPLOAD_DIR):
            return
        now = time.time()
        for session_folder in os.listdir(UPLOAD_DIR):
            folder_path = os.path.join(UPLOAD_DIR, session_folder)
            if os.path.isdir(folder_path):
                # If older than 2 hours
                if os.stat(folder_path).st_mtime < now - (2 * 3600):
                    shutil.rmtree(folder_path, ignore_errors=True)
    except Exception:
        pass

@router.post("/upload")
def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    # Trigger background cleanup asynchronously
    background_tasks.add_task(cleanup_old_sessions)

    # Validate session_id
    clean_session_id = sanitize_session_id(session_id)

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type '{ext}'. Allowed types: CSV, Excel (.xlsx, .xls), and SQLite (.db, .sqlite)"
        )

    saved_path = save_uploaded_file(file, clean_session_id)
    db_path = create_sqlite_database(saved_path, clean_session_id)

    schema = extract_schema(db_path)

    return {
        "filename": os.path.basename(file.filename),
        "schema": schema,
        "status": "indexed"
    }

@router.post("/ask")
def ask_question(request: AskRequest):
    return generate_sql(request.question, request.schema_data, request.api_key)

@router.post("/execute")
def execute_sql_endpoint(request: ExecuteRequest):
    clean_session_id = sanitize_session_id(request.session_id)
    db_path = os.path.join(UPLOAD_DIR, clean_session_id, f"{clean_session_id}.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404, 
            detail="Session database not found. Please upload your file first."
        )

    result = execute_query(db_path, request.query)

    if isinstance(result, str):
        # Database execution returned an error message
        raise HTTPException(status_code=400, detail=result)

    return {"data": result}