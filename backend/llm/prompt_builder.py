def build_prompt(
    question: str,
    schema: list
):
    schema_text = "\n".join(
        [
            f"{col['name']} ({col['type']})"
            for col in schema
        ]
    )

    return f"""
You are an expert SQL generator.

Rules:
- Return only SQL
- Use table name: data
- Only generate SELECT statements
- Do not explain anything

Schema:
{schema_text}

Question:
{question}
"""