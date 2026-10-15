import os
import re
import sys

# Ensure backend directory is in sys.path for direct or package execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from llm.prompt_builder import build_prompt
from llm.gemini_provider import generate_sql_from_gemini

def validate_sql(query: str) -> tuple[bool, str]:
    """Validates the generated SQL to ensure it is safe and is a read-only query (SELECT / WITH)."""
    if not query or not query.strip():
        return False, "Empty query generated."

    query_stripped = query.strip()
    query_upper = query_stripped.upper()

    # Allow SELECT and CTE (WITH ... SELECT) queries
    if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
        return False, "Only SELECT and WITH (CTE) read queries are allowed."

    # Strip out string literals so data values like 'UPDATE' or 'DELETE' don't trigger false positives
    cleaned_for_check = re.sub(r"'[^']*'", "''", query_upper)
    cleaned_for_check = re.sub(r'"[^"]*"', '""', cleaned_for_check)

    forbidden_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "CREATE", "TRUNCATE", "EXEC", "PRAGMA", "ATTACH", "DETACH"
    ]

    for keyword in forbidden_keywords:
        if re.search(rf'\b{keyword}\b', cleaned_for_check):
            return False, f"Unsafe operation detected: '{keyword}' is not allowed in read-only mode."

    return True, "Valid"

def extract_sql_from_response(raw_text: str) -> str:
    """Robustly extracts SQL query from markdown fences or plain text."""
    # Try finding content inside ```sql ... ``` or ``` ... ```
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", raw_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If no fences, remove any standalone backticks and trim
    return raw_text.replace("```sql", "").replace("```", "").strip()

def generate_sql(question: str, schema: list, api_key: str = None):
    prompt = build_prompt(question, schema)
    
    if not api_key:
        return {
            "sql": "",
            "is_valid": False,
            "validation_message": "Please provide a valid Gemini API Key."
        }

    try:
        raw_response = generate_sql_from_gemini(prompt, api_key)
        cleaned_sql = extract_sql_from_response(raw_response)

        is_valid, message = validate_sql(cleaned_sql)

        return {
            "sql": cleaned_sql,
            "is_valid": is_valid,
            "validation_message": message
        }
    except Exception as e:
        return {
            "sql": "",
            "is_valid": False,
            "validation_message": str(e)
        }