# -----------------------------
# BASE ICU (exemple)
# -----------------------------
ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation en réanimation, intubation, ventilation mécanique, agitation",
        "effets": "dépression respiratoire, hypotension, sédation profonde, amnésie",
        "surveillance": "TA, FR, saturation, score de sédation (RASS)",
        "points_icu": "accumulation en perfusion prolongée, risque de sevrage"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation en réanimation",
        "effets": "hypotension, bradycardie, dépression respiratoire",
        "surveillance": "TA, triglycérides, niveau de sédation",
        "points_icu": "risque syndrome de perfusion prolongée"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension",
        "effets": "vasoconstriction, augmentation TA",
        "surveillance": "TA invasive, perfusion périphérique",
        "points_icu": "voie centrale recommandée"
    }
}

# -----------------------------
# RAG ENGINE
# -----------------------------
def search_icu(query: str) -> str:

    if not query:
        return ""

    # normalisation forte
    q = query.lower().strip()
    q_clean = q.replace(" ", "")

    results = []

    for drug, data in ICU_DATABASE.items():

        drug_key = drug.lower()
        drug_clean = drug_key.replace(" ", "")

        # 🔥 MATCH ROBUSTE (clé du problème résolu ici)
        if (
            drug_key in q
            or q in drug_key
            or drug_clean in q_clean
            or q_clean in drug_clean
            or any(word in q for word in drug_key.split())
        ):
            results.append(f"""
MÉDICAMENT : {drug}

Classe : {data['classe']}
Usage : {data['usage']}
Effets : {data['effets']}
Surveillance : {data['surveillance']}
Points ICU : {data['points_icu']}
""")

    # si rien trouvé → retour vide propre (important pour app.py)
    return "\n---------------------\n".join(results)
