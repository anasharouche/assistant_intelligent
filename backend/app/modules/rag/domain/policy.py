from __future__ import annotations
from dataclasses import dataclass
from typing import List
import re

from .models import RetrievedContext


@dataclass(frozen=True)
class BusinessPolicyConfig:
    rule_keywords: tuple[str, ...] = (
        "absence",
        "retard",
        "assiduité",
        "ponctualité",
        "doit",
        "doivent",
        "obligatoire",
        "autorisé",
        "autorisée",
        "justifiée",
        "justifié",
        "validation",
    )
    max_sentences: int = 4
    min_sentence_len: int = 25
    fallback_mode: str = "I_DONT_KNOW"


class RagBusinessPolicy:
    """
    Politique métier RAG :
    extraire une règle administrative complète et exploitable.
    """

    def __init__(self, cfg: BusinessPolicyConfig | None = None) -> None:
        self.cfg = cfg or BusinessPolicyConfig()

    def select_normative_contexts(
        self,
        contexts: List[RetrievedContext],
    ) -> List[RetrievedContext]:
        kws = tuple(k.lower() for k in self.cfg.rule_keywords)
        return [
            c for c in contexts
            if any(k in (c.text or "").lower() for k in kws)
        ]

    def extract_normative_rule(
        self,
        contexts: List[RetrievedContext],
    ) -> str | None:
        if not contexts:
            return None

        best = max(contexts, key=lambda c: c.score)

        sentences = re.split(r"(?<=[.!?])\s+|\n+", best.text)
        selected: list[str] = []

        kws = tuple(k.lower() for k in self.cfg.rule_keywords)

        for s in sentences:
            s = s.strip()
            if len(s) < self.cfg.min_sentence_len:
                continue
            if any(k in s.lower() for k in kws):
                selected.append(s)
            if len(selected) >= self.cfg.max_sentences:
                break

        if not selected:
            return None

        rule = " ".join(selected)
        return f"{rule} (page {best.page})"

    def fallback(self) -> str:
        return "Je ne sais pas."


def select_normative_rule(contexts: List[RetrievedContext]) -> str | None:
    policy = RagBusinessPolicy()
    filtered = policy.select_normative_contexts(contexts)
    return policy.extract_normative_rule(filtered)
