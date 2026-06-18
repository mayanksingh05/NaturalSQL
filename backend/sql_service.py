from llm.prompt_builder import build_prompt


def generate_sql(
    question: str,
    schema: list
):
    prompt = build_prompt(
        question,
        schema
    )

    return {
        "prompt": prompt
    }