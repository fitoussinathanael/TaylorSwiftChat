# -----------------------------
# BASE ICU
# -----------------------------
ICU_DATABASE = {

    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU, agitation, intubation",
        "effets": "dépression respiratoire, hypotension",
        "surveillance": "TA, FR, RASS",
        "points_icu": "accumulation en perfusion prolongée, risque sevrage"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation patient ventilé",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, sédation",
        "points_icu": "risque syndrome propofol"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie ICU",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation en perfusion prolongée"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction",
        "surveillance": "TA invasive, perfusion périphérique",
        "points_icu": "voie centrale recommandée"
    },

    "potassium": {
        "classe": "électrolyte",
        "usage": "hypokaliémie",
        "effets": "troubles du rythme",
        "surveillance": "ECG, kaliémie",
        "points_icu": "perfusion lente obligatoire"
    }
}

# -----------------------------
# SYNONYMES
# -----------------------------
ALIASES = {
    "midaz": "midazolam",
    "nora": "noradrenaline",
    "kcl": "potassium",
    "fenta": "fentanyl",
    "propof": "propofol"
}

# -----------------------------
# SEARCH ICU
# -----------------------------
def search_icu(query: str):

    if not query:
        return None

    q = query.lower().strip().replace(" ", "")

    # alias mapping
    for alias, real in ALIASES.items():
        if alias in q:
            q = q.replace(alias, real)

    for drug, data in ICU_DATABASE.items():

        drug_key = drug.lower().replace(" ", "")

        if drug_key in q or q in drug_key:
            return data

    return None
