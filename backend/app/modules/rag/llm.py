import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def call_llm(prompt: str) -> str:
    """
    Appel du LLM local via Ollama
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"Erreur Ollama : {response.text}")

    return response.json()["response"]
