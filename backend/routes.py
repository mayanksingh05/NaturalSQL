from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import shutil
import time
from database import (
    save_uploaded_file,
    create_sqlite_database,
    extract_schema,
    execute_query,
    UPLOAD_DIR
)
from sql_service import generate_sql

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".db"}

class AskRequest(BaseModel):
    question: str
    api_key: str
    session_id: str
    schema_data: list

class ExecuteRequest(BaseModel):
    query: str
    session_id: str

def cleanup_old_sessions():
    """Deletes session folders older than 2 hours to free up Render storage."""
    now = time.time()
    for session_folder in os.listdir(UPLOAD_DIR):
        folder_path = os.path.join(UPLOAD_DIR, session_folder)
        if os.path.isdir(folder_path):
            if os.stat(folder_path).st_mtime < now - (2 * 3600):
                shutil.rmtree(folder_path, ignore_errors=True)

@router.post("/upload")
def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    # Trigger background cleanup asynchronously
    background_tasks.add_task(cleanup_old_sessions)

    # Security: File type validation
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV, Excel, and DB allowed.")

    saved_path = save_uploaded_file(file, session_id)
    db_path = create_sqlite_database(saved_path, session_id)

    if not db_path:
        raise HTTPException(status_code=400, detail="Failed to process file.")

    schema = extract_schema(db_path)

    return {
        "filename": file.filename,
        "schema": schema,
        "status": "indexed"
    }

@router.post("/ask")
def ask_question(request: AskRequest):
    # Pass the schema directly from the frontend request, not globals
    return generate_sql(request.question, request.schema_data, request.api_key)

@router.post("/execute")
def execute_sql_endpoint(request: ExecuteRequest):
    db_path = os.path.join(UPLOAD_DIR, request.session_id, f"{request.session_id}.db")
    
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Session expired or database not found. Please re-upload your file.")

    result = execute_query(db_path, request.query)

    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {"data": result}