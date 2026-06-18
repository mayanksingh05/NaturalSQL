from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from pydantic import BaseModel

from database import save_uploaded_file

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(
    request: AskRequest
):
    return {
        "sql": """
SELECT customer_name,
       SUM(expense)
FROM sales
GROUP BY customer_name
ORDER BY SUM(expense) DESC
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

    return {
        "filename": file.filename,
        "path": saved_path,
        "status": "uploaded"
    }