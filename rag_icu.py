# rag_icu.py

# -----------------------------
# ICU RAG SIMPLE (VERSION SAFE)
# -----------------------------
# Objectif : ne JAMAIS casser l'app Streamlit
# Pas de dépendances externes lourdes

# -----------------------------
# BASE ICU SIMPLE (HUG EXEMPLE)
# -----------------------------
ICU_DATABASE = {
    "midazolam": {
        "compatibility": "Variable selon concentrations. Données ICU nécessaires.",
        "note": "Hypotension possible en association avec sédatifs/vasopresseurs."
    },
    "noradrenaline": {
        "compatibility": "Compatible avec plusieurs sédatifs en Y-site selon protocoles ICU.",
        "note": "Vasopresseur majeur en choc septique."
    },
    "fentanyl": {
        "compatibility": "Compatible fréquente en réanimation avec sédatifs IV.",
        "note": "Analgésie forte, surveillance dépression respiratoire."
    },
    "propofol": {
        "compatibility": "Compatible avec de nombreux agents ICU selon dilution.",
        "note": "Risque hypotension + hypertriglycéridémie."
    }
}

# -----------------------------
# SIMPLE SEARCH ENGINE
# -----------------------------
def search_icu(query: str) -> str:
    """
    RAG ICU minimal :
    - pas d'embeddings
    - pas de libs externes
    - recherche par mots-clés
    """

    if not query:
        return "Aucune donnée fournie."

    query_lower = query.lower()

    results = []

    for key, data in ICU_DATABASE.items():
        if key in query_lower:
            results.append(
                f"""
MÉDICAMENT: {key}

Compatibilité:
{data['compatibility']}

Note ICU:
{data['note']}
"""
            )

    # -----------------------------
    # SI AUCUN RESULTAT
    # -----------------------------
    if not results:
        return "Aucune donnée ICU trouvée dans la base locale."

    return "\n---\n".join(results)
