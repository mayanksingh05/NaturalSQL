def build_prompt(
    question: str,
    schema: list
) -> str:
    # Group columns by their respective table names
    tables = {}
    for col in schema:
        table_name = col.get("table", "data")
        tables.setdefault(table_name, []).append(f"{col['name']} ({col.get('type', 'TEXT')})")

    schema_lines = []
    for table_name, columns in tables.items():
        col_list = ", ".join(columns)
        schema_lines.append(f"Table '{table_name}': [{col_list}]")

    schema_text = "\n".join(schema_lines)

    return f"""You are an expert SQL generator for SQLite.

Return ONLY a single valid SQLite SQL query.

Rules:
- Query only from the table(s) defined in the Schema below.
- Use the exact table and column names as provided in the Schema.
- If multiple tables need to be joined, use proper SQL JOIN syntax.
- Do NOT make assumptions about columns that are not listed.
- Never explain your output.
- Never wrap the query in markdown or code blocks (no ``` or ```sql).
- Only generate SELECT statements (or WITH ... SELECT statements).

Database Schema:
{schema_text}

User Question:
{question}
"""