# rag_icu.py

# -----------------------------
# MINI BASE ICU STRUCTURÉE
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, intubation, ventilation mécanique, agitation",
        "effets": "sédation, amnésie, dépression respiratoire, hypotension",
        "surveillance": "FR, TA, score de sédation (RASS), conscience",
        "points_icu": "accumulation en perfusion prolongée, risque de sevrage"
    },

    "noradrenaline": {
        "classe": "vasopresseur alpha-adrénergique",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique, extravasation",
        "points_icu": "voie centrale recommandée, risque nécrose si extravasation"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie en réanimation, patient intubé",
        "effets": "analgésie, dépression respiratoire, bradycardie",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation si perfusion prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation en réanimation",
        "effets": "hypotension, bradycardie, dépression respiratoire",
        "surveillance": "TA, triglycérides, profondeur sédation",
        "points_icu": "risque syndrome de perfusion prolongée"
    },

    "ceftriaxone": {
        "classe": "céphalosporine 3e génération",
        "usage": "infection sévère, sepsis",
        "effets": "allergie, troubles digestifs",
        "surveillance": "infection, fonction rénale",
        "points_icu": "interaction avec calcium IV (risque précipitation)"
    },

    "calcium": {
        "classe": "électrolyte",
        "usage": "hypocalcémie, réanimation",
        "effets": "troubles du rythme si surdosage",
        "surveillance": "ECG, calcémie",
        "points_icu": "NE PAS mélanger avec ceftriaxone IV"
    }
}


# -----------------------------
# SEARCH ICU (RAG SIMPLE MAIS FIABLE)
# -----------------------------

def search_icu(query: str) -> str:
    """
    RAG ICU V1 :
    - matching simple mais fiable
    - sortie structurée pour LLM
    """

    if not query:
        return "Aucune donnée fournie."

    q = query.lower()
    results = []

    for drug, data in ICU_DATABASE.items():

        # matching robuste (évite les faux négatifs simples)
        if drug in q or any(word == drug for word in q.split()):

            results.append(f"""
MÉDICAMENT: {drug}

Classe: {data['classe']}
Usage ICU: {data['usage']}
Effets: {data['effets']}
Surveillance: {data['surveillance']}
Points critiques ICU: {data['points_icu']}
""")

    if not results:
        return "⚠️ Aucune donnée ICU locale trouvée dans la base."

    return "\n----------------------\n".join(results)
