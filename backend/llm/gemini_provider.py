import google.generativeai as genai

def generate_sql_from_gemini(prompt: str, api_key: str) -> str:
    """Generates SQL using the Gemini API via user-provided key."""
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is missing. Please provide a valid key.")

    # Configure client with user's key
    genai.configure(api_key=api_key.strip())

    # Try gemini-1.5-flash first (fast, high free-tier rate limits), fallback to gemini-1.5-pro
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro']
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Safely extract text
            try:
                if response.text:
                    return response.text.strip()
            except (ValueError, AttributeError):
                if response.candidates and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text.strip()
                raise ValueError("Model response was empty or blocked by safety filters.")

        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Gemini API Error: {str(last_error)}")