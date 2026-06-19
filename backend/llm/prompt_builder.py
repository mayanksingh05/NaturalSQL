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
You are an SQL generator.

Return ONLY SQL.

Rules:
- Use table name data
- Use only columns from schema
- Generate valid SQLite SQL
- Never explain
- Never use markdown
- Never use code fences
- Return only a SELECT statement

Schema:
{schema_text}

Question:
{question}
"""