import re
from llm.prompt_builder import build_prompt
from llm.gemini_provider import generate_sql_from_gemini

def validate_sql(query: str) -> tuple[bool, str]:
    """Validates the generated SQL to ensure it is safe and is a SELECT statement."""
    query_upper = query.upper()

    if not query_upper.strip().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    forbidden_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "CREATE", "TRUNCATE", "EXEC", "PRAGMA"
    ]

    for keyword in forbidden_keywords:
        if re.search(rf'\b{keyword}\b', query_upper):
            return False, f"Unsafe keyword detected: {keyword}. Query rejected."

    return True, "Valid"

def generate_sql(question: str, schema: list, api_key: str = None):
    prompt = build_prompt(question, schema)
    
    if not api_key:
        return {
            "sql": "",
            "is_valid": False,
            "validation_message": "Please provide a valid Gemini API Key."
        }

    try:
        # Strictly using Gemini Provider now
        generated_sql = generate_sql_from_gemini(prompt, api_key)

        # Clean up markdown formatting the LLM might add
        cleaned_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

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