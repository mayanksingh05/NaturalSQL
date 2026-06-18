from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from pydantic import BaseModel

from database import (
    save_uploaded_file,
    create_sqlite_database,
    extract_schema
)

from sql_service import generate_sql

router = APIRouter()

CURRENT_SCHEMA = []


class AskRequest(BaseModel):
    question: str


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...)
):
    global CURRENT_SCHEMA

    saved_path = save_uploaded_file(
        file
    )

    db_path = create_sqlite_database(
        saved_path
    )

    schema = extract_schema(
        db_path
    )

    CURRENT_SCHEMA = schema

    return {
        "filename": file.filename,
        "schema": schema,
        "status": "indexed"
    }


@router.post("/ask")
def ask_question(
    request: AskRequest
):
    return generate_sql(
        request.question,
        CURRENT_SCHEMA
    )