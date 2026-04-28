# rag_icu.py

# -----------------------------
# MINI BASE ICU ENRICHI (V1)
# -----------------------------
# objectif : stabilité + contenu clinique utile

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, intubation, agitation, ventilation mécanique",
        "effets": "sédation, amnésie, dépression respiratoire, hypotension",
        "surveillance": "score de sédation, FR, TA, saturation",
        "points_icu": "accumulation possible en perfusion prolongée, attention sevrage"
    },

    "noradrenaline": {
        "classe": "vasopresseur alpha-adrénergique",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique, extravasation",
        "points_icu": "voie centrale préférée, surveillance nécrose extravasation"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie réanimation, patient intubé",
        "effets": "analgésie, dépression respiratoire, bradycardie",
        "surveillance": "FR, sédation, douleur",
        "points_icu": "accumulation si perfusion prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation en réanimation",
        "effets": "hypotension, bradycardie, dépression respiratoire",
        "surveillance": "TA, triglycérides, niveau de sédation",
        "points_icu": "risque syndrome propofol infusion (longues perfusions)"
    },

    "ceftriaxone": {
        "classe": "céphalosporine 3e génération",
        "usage": "infection sévère, sepsis",
        "effets": "allergie, troubles digestifs",
        "surveillance": "clinique infectieuse, fonction rénale",
        "points_icu": "attention interactions calcium IV (précipitation)"
    },

    "calcium": {
        "classe": "électrolyte",
        "usage": "hypocalcémie, réanimation",
        "effets": "arythmies si surdosage",
        "surveillance": "ECG, calcémie",
        "points_icu": "NE PAS mélanger avec ceftriaxone IV (risque précipitation)"
    }
}

# -----------------------------
# SIMPLE SEARCH ENGINE
# -----------------------------
def search_icu(query: str) -> str:
    """
    RAG ICU V1 :
    - recherche simple par mot-clé
    - base enrichie clinique
    """

    if not query:
        return "Aucune donnée fournie."

    q = query.lower()
    results = []

    for drug, data in ICU_DATABASE.items():
        if drug in q:
            results.append(f"""
MÉDICAMENT: {drug}

Classe: {data['classe']}
Usage ICU: {data['usage']}
Effets: {data['effets']}
Surveillance: {data['surveillance']}
Points ICU: {data['points_icu']}
""")

    if not results:
        return "Aucune donnée ICU trouvée dans la base locale."

    return "\n----------------------\n".join(results)
