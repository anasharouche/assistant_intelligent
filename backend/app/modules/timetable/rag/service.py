from __future__ import annotations

from app.modules.rag.infrastructure.vector_store_faiss import retrieve_context
from app.modules.rag.infrastructure.llm_gateway import get_llm_gateway
from app.modules.timetable.rag.prompts import TIMETABLE_PROMPT


def ask_timetable(*, question: str, group_id: int) -> str:
    namespace = f"timetable_group_{group_id}"

    contexts, _sources = retrieve_context(
        question,
        k=5,
        namespace=namespace,
    )

    # Si aucun contexte => logique métier stricte
    if not contexts:
        return "Je ne sais pas."

    # Concat propre (on met page + extrait)
    context_text = "\n\n".join(
        f"(page {c['page']}) {c['text']}"
        for c in contexts
        if c.get("text")
    ).strip()

    if not context_text:
        return "Je ne sais pas."

    prompt = TIMETABLE_PROMPT.format(
        context=context_text,
        question=question,
    )

    llm = get_llm_gateway()
    answer = llm.generate(prompt).strip()

    # Sécurité : si le modèle répond vide
    if not answer:
        return "Je ne sais pas."

    return answer
