# -----------------------------
# BASE ICU SIMPLE
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, ventilation mécanique",
        "effets": "dépression respiratoire, hypotension, sédation",
        "surveillance": "TA, FR, saturation, score RASS",
        "points_icu": "accumulation en perfusion prolongée"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique",
        "points_icu": "voie centrale recommandée"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie ICU",
        "effets": "dépression respiratoire",
        "surveillance": "FR, sédation",
        "points_icu": "accumulation prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation ICU",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides",
        "points_icu": "risque infusion prolongée"
    },

    "ceftriaxone": {
        "classe": "céphalosporine",
        "usage": "infection sévère",
        "effets": "allergie, troubles digestifs",
        "surveillance": "clinique infectieuse",
        "points_icu": "interaction calcium IV"
    },

    "ibuprofene": {
        "classe": "AINS",
        "usage": "antalgique / antipyrétique",
        "effets": "insuffisance rénale, troubles digestifs",
        "surveillance": "fonction rénale",
        "points_icu": "risque rénal en déshydratation"
    }
}

# -----------------------------
# SEARCH SIMPLE RAG
# -----------------------------

def search_icu(query: str) -> str:

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
        return "Aucune donnée ICU trouvée dans la base."

    return "\n---------------------\n".join(results)
