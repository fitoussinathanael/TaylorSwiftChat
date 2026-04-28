# rag_icu.py

# -----------------------------
# BASE ICU (STRUCTURÉE)
# -----------------------------

ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, ventilation mécanique, agitation",
        "effets": "dépression respiratoire, hypotension, sédation",
        "surveillance": "TA, FR, saturation, score RASS",
        "points_icu": "accumulation en perfusion prolongée, risque sevrage"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique, extravasation",
        "points_icu": "voie centrale recommandée"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie en réanimation",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, sédation, douleur",
        "points_icu": "accumulation en perfusion prolongée"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation en réanimation",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, niveau de sédation",
        "points_icu": "risque syndrome infusion prolongée"
    },

    "ceftriaxone": {
        "classe": "antibiotique céphalosporine",
        "usage": "infection sévère / sepsis",
        "effets": "allergies, troubles digestifs",
        "surveillance": "clinique infectieuse, fonction rénale",
        "points_icu": "interaction calcium IV (précipitation)"
    },

    "ibuprofene": {
        "classe": "AINS",
        "usage": "antalgique / antipyrétique",
        "effets": "insuffisance rénale, gastrite, risque hémorragique",
        "surveillance": "fonction rénale, douleur, température",
        "points_icu": "risque rénal en hypovolémie"
    }
}

# -----------------------------
# RAG ROBUSTE (MATCH INTELLIGENT SIMPLE)
# -----------------------------

def search_icu(query: str) -> str:

    if not query:
        return "Aucune donnée fournie."

    q = query.lower().strip()

    results = []

    for drug, data in ICU_DATABASE.items():

        # MATCH ROBUSTE :
        # - mot exact
        # - ou inclusion partielle
        # - ou mots composés
        drug_words = drug.split("/")

        if (
            drug in q
            or any(word in q for word in drug_words)
            or any(q in word for word in drug_words)
        ):

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
