from llm.prompt_builder import build_prompt
from llm.ollama_provider import generate_sql_from_ollama


def generate_sql(
    question: str,
    schema: list
):
    prompt = build_prompt(
        question,
        schema
    )

    generated_sql = generate_sql_from_ollama(
        prompt
    )

    return {
        "sql": generated_sql
    }