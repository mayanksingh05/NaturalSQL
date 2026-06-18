from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from pydantic import BaseModel

from database import (
    save_uploaded_file,
    create_sqlite_database,
    extract_schema
)

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(
    request: AskRequest
):
    return {
        "sql": """
SELECT *
FROM data
LIMIT 10;
""".strip()
    }


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...)
):
    saved_path = save_uploaded_file(
        file
    )

    db_path = create_sqlite_database(
        saved_path
    )

    schema = extract_schema(
        db_path
    )

    return {
        "filename": file.filename,
        "database": db_path,
        "schema": schema,
        "status": "indexed"
    }