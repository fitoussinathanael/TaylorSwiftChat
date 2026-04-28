# rag_icu.py

# -----------------------------
# BASE ICU SIMPLE (V1 STABLE)
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, intubation, ventilation mécanique",
        "effets": "sédation, amnésie, dépression respiratoire, hypotension",
        "surveillance": "TA, FR, score de sédation (RASS)",
        "points_icu": "accumulation en perfusion prolongée, risque de sevrage"
    },

    "noradrenaline": {
        "classe": "vasopresseur alpha-adrénergique",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation tension artérielle",
        "surveillance": "TA invasive, perfusion périphérique, extravasation",
        "points_icu": "voie centrale recommandée, risque nécrose extravasation"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie en réanimation",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation si perfusion prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation en réanimation",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, profondeur sédation",
        "points_icu": "risque syndrome de perfusion prolongée"
    },

    "ceftriaxone": {
        "classe": "céphalosporine 3e génération",
        "usage": "infection sévère",
        "effets": "allergie, troubles digestifs",
        "surveillance": "clinique infectieuse, fonction rénale",
        "points_icu": "interaction calcium IV (risque précipitation)"
    },

    "calcium": {
        "classe": "électrolyte",
        "usage": "hypocalcémie",
        "effets": "troubles du rythme si excès",
        "surveillance": "ECG, calcémie",
        "points_icu": "NE PAS mélanger avec ceftriaxone IV"
    }
}


# -----------------------------
# RAG SIMPLE MAIS ROBUSTE
# -----------------------------

def search_icu(query: str) -> str:
    """
    RAG ICU V1 stable :
    - matching simple robuste
    - sortie structurée pour LLM
    """

    if not query:
        return "Aucune donnée fournie."

    q = query.lower().strip()

    results = []

    for drug, data in ICU_DATABASE.items():

        drug_clean = drug.lower().strip()

        # MATCH ROBUSTE
        if drug_clean in q:

            results.append(f"""
MÉDICAMENT: {drug}

Classe: {data['classe']}
Usage ICU: {data['usage']}
Effets: {data['effets']}
Surveillance: {data['surveillance']}
Points ICU: {data['points_icu']}
""")

    if not results:
        return "⚠️ Aucune donnée ICU locale trouvée dans la base."

    return "\n----------------------\n".join(results)
