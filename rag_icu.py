# -----------------------------
# BASE ICU
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU",
        "effets": "dépression respiratoire",
        "surveillance": "TA, FR, RASS",
        "points_icu": "accumulation"
    }
}

# -----------------------------
# RAG FUNCTION (TU REMPLACES ICI)
# -----------------------------

def search_icu(query: str) -> str:

    if not query:
        return "Aucune donnée fournie."

    q = query.lower().strip()

    results = []

    for drug, data in ICU_DATABASE.items():

        drug_key = drug.lower()

        match = (
            drug_key in q
            or q in drug_key
            or any(word in q for word in drug_key.split())
        )

        if match:

            results.append(f"""
MÉDICAMENT : {drug}

Classe : {data['classe']}
Usage : {data['usage']}
Effets : {data['effets']}
Surveillance : {data['surveillance']}
Points ICU : {data['points_icu']}
""")

    if not results:
        return "Aucune donnée ICU trouvée dans la base."

    return "\n---------------------\n".join(results)
