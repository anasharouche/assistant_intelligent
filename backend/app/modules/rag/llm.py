import httpx
from app.core.config import settings


def call_llm(prompt: str) -> str:
    """
    Appelle un LLM LOCAL via Ollama.
    Requiert: Ollama en local (http://localhost:11434)
    """
    base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
    model = getattr(settings, "ollama_model", "llama3.1")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        resp = httpx.post(f"{base_url}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("response") or "").strip() or "Je ne sais pas."
    except Exception:
        # Fallback safe (pas de crash API)
        return "Je ne sais pas (erreur lors de l'appel au modèle local)."
