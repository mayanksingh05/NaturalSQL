from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from database import (
    save_uploaded_file,
    create_sqlite_database,
    extract_schema,
    execute_query
)
from sql_service import generate_sql

router = APIRouter()

CURRENT_SCHEMA = []
CURRENT_DB_PATH = None

class AskRequest(BaseModel):
    question: str
    api_key: str = None  # Added API Key field

class ExecuteRequest(BaseModel):
    query: str

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    global CURRENT_SCHEMA, CURRENT_DB_PATH

    saved_path = save_uploaded_file(file)
    db_path = create_sqlite_database(saved_path)

    if not db_path:
        raise HTTPException(status_code=400, detail="Failed to process file.")

    CURRENT_DB_PATH = db_path
    schema = extract_schema(db_path)
    CURRENT_SCHEMA = schema

    return {
        "filename": file.filename,
        "schema": schema,
        "status": "indexed"
    }

@router.post("/ask")
def ask_question(request: AskRequest):
    # Pass the API key to the SQL service
    return generate_sql(request.question, CURRENT_SCHEMA, request.api_key)

@router.post("/execute")
def execute_sql_endpoint(request: ExecuteRequest):
    if not CURRENT_DB_PATH:
        raise HTTPException(status_code=400, detail="No database loaded. Please upload a file first.")

    result = execute_query(CURRENT_DB_PATH, request.query)

    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {"data": result}