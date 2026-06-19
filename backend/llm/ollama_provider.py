import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "zephyr-local:latest"


def generate_sql_from_ollama(
    prompt: str
):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["response"].strip()