from __future__ import annotations
from typing import Optional
import subprocess


# =========================
# INTERFACE
# =========================
class LlmGateway:
    """
    Interface LLM.
    Le métier dépend uniquement de cette interface.
    """

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


# =========================
# FALLBACK
# =========================
class LocalFallbackGateway(LlmGateway):
    """
    Utilisé si le LLM est indisponible.
    """

    def __init__(self, message: str = "Je ne sais pas (modèle indisponible).") -> None:
        self.message = message

    def generate(self, prompt: str) -> str:
        return self.message


# =========================
# OLLAMA GATEWAY (LOCAL)
# =========================
class OllamaGateway(LlmGateway):
    """
    Adaptateur vers Ollama en local.
    Compatible avec mistral, llama3, phi, etc.
    Corrige explicitement les problèmes d'encodage UTF-8 sous Windows.
    """

    def __init__(self, model: str = "mistral") -> None:
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            process = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode("utf-8"),   # ✅ UTF-8 explicite
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            # ✅ Décodage UTF-8 sûr
            return process.stdout.decode("utf-8", errors="ignore").strip()

        except Exception as e:
            return "Je ne sais pas (erreur lors de l'appel au modèle local)."


# =========================
# ADAPTATEUR VERS ANCIEN call_llm
# =========================
class ExistingCallLlmGateway(LlmGateway):
    """
    Permet de brancher un ancien call_llm(prompt).
    """

    def __init__(self, call_llm_func) -> None:
        self._call = call_llm_func

    def generate(self, prompt: str) -> str:
        try:
            result = self._call(prompt)
            return str(result).encode("utf-8", errors="ignore").decode("utf-8")
        except Exception:
            return "Je ne sais pas."


# =========================
# FACTORY (RECOMMANDÉ)
# =========================
def get_llm_gateway() -> LlmGateway:
    """
    Point unique de décision.
    Tu peux changer de modèle ici sans toucher au métier.
    """
    try:
        return OllamaGateway(model="mistral")
    except Exception:
        return LocalFallbackGateway()
