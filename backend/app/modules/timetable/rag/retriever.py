from app.modules.rag.core.vector_store import vector_store


def retrieve(
    *,
    query: str,
    namespace: str,
    top_k: int = 5,
) -> list[str]:
    """
    Récupère les passages les plus pertinents depuis le vector store.
    """
    results = vector_store.similarity_search(
        query=query,
        namespace=namespace,
        k=top_k,
    )

    # On retourne uniquement le texte
    return [doc.page_content for doc in results]
