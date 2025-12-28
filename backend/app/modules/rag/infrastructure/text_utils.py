def normalize_text(text: str) -> str:
    """
    Nettoyage UTF-8 robuste pour texte extrait de PDF.
    - Corrige encodage cassé
    - Supprime caractères invisibles
    - Préserve le contenu métier/juridique
    """
    if not text:
        return ""

    # Force UTF-8
    text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    # Supprime caractères non imprimables
    text = "".join(c for c in text if c.isprintable() or c in "\n\t")

    # Nettoyage espaces multiples
    text = " ".join(text.split())

    return text.strip()
