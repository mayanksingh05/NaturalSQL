import google.generativeai as genai

def generate_sql_from_gemini(prompt: str, api_key: str) -> str:
    """Generates SQL using the Gemini API via user-provided key."""
    if not api_key:
        raise ValueError("Gemini API key is missing.")

    # Configure the API client with the user's specific key
    genai.configure(api_key=api_key)

    # Using Gemini 1.5 Pro as it is the best model for coding and SQL tasks
    model = genai.GenerativeModel('gemini-1.5-pro')

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")