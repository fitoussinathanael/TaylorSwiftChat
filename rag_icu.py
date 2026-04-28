# rag_icu.py

# -----------------------------
# BASE ICU SIMPLE ET STABLE
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, ventilation mécanique, agitation",
        "effets": "sédation, dépression respiratoire, hypotension",
        "surveillance": "TA, FR, saturation, score RASS",
        "points_icu": "accumulation en perfusion prolongée, risque sevrage"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique",
        "points_icu": "voie centrale recommandée, extravasation"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie en réanimation",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, sédation, douleur",
        "points_icu": "accumulation si perfusion prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation ICU",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, sédation",
        "points_icu": "risque infusion prolongée"
    },

    "ceftriaxone": {
        "classe": "céphalosporine",
        "usage": "infection sévère",
        "effets": "allergie, troubles digestifs",
        "surveillance": "clinique infectieuse",
        "points_icu": "interaction calcium IV"
    }
}

# -----------------------------
# RAG SIMPLE (ROBUSTE)
# -----------------------------

def search_icu(query: str) -> str:
    """
    Recherche ICU simple :
    - matching par mot-clé
    - stable Streamlit
    """

    if not query:
        return "Aucune donnée fournie."

    q = query.lower().strip()

    results = []

    for drug, data in ICU_DATABASE.items():

        if drug in q:

            results.append(f"""
MÉDICAMENT : {drug}

Classe : {data['classe']}
Usage : {data['usage']}
Effets : {data['effets']}
Surveillance : {data['surveillance']}
Points ICU : {data['points_icu']}
""")

    if not results:
        return "⚠️ Aucune donnée ICU locale trouvée."

    return "\n---------------------\n".join(results)
