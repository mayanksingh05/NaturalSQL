from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: AskRequest):

    return {
        "sql": """
SELECT customer_name,
       SUM(expense) AS total_expense
FROM sales
GROUP BY customer_name
ORDER BY total_expense DESC
LIMIT 10;
""".strip()
    }