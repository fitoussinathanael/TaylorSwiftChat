# -----------------------------
# BASE ICU (V2)
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
        "points_icu": "risque syndrome perfusion propofol"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie ICU",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation en perfusion prolongée"
    },

    "morphine": {
        "classe": "opioïde",
        "usage": "analgésie",
        "effets": "dépression respiratoire, hypotension",
        "surveillance": "FR, douleur, conscience",
        "points_icu": "prudence insuffisance rénale"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction",
        "surveillance": "TA invasive, perfusion périphérique",
        "points_icu": "voie centrale recommandée, extravasation"
    },

    "dobutamine": {
        "classe": "inotrope",
        "usage": "choc cardiogénique",
        "effets": "tachycardie",
        "surveillance": "FC, TA",
        "points_icu": "risque arythmie"
    },

    "adrenaline": {
        "classe": "catécholamine",
        "usage": "arrêt cardiaque, choc",
        "effets": "tachycardie, HTA",
        "surveillance": "ECG, TA",
        "points_icu": "risque arythmie"
    },

    "ceftriaxone": {
        "classe": "antibiotique",
        "usage": "infection sévère",
        "effets": "allergie",
        "surveillance": "clinique, biologique",
        "points_icu": "ne pas mélanger avec calcium IV"
    },

    "piperacilline": {
        "classe": "antibiotique",
        "usage": "infection nosocomiale",
        "effets": "allergie",
        "surveillance": "clinique",
        "points_icu": "adapter fonction rénale"
    },

    "potassium": {
        "classe": "électrolyte",
        "usage": "hypokaliémie",
        "effets": "troubles du rythme",
        "surveillance": "ECG, kaliémie",
        "points_icu": "perfusion lente obligatoire"
    },

    "calcium": {
        "classe": "électrolyte",
        "usage": "hypocalcémie",
        "effets": "arythmies",
        "surveillance": "ECG, calcémie",
        "points_icu": "incompatibilité avec ceftriaxone IV"
    }
}

# -----------------------------
# SYNONYMES / ABLÉVIATIONS
# -----------------------------
ALIASES = {
    "nora": "noradrenaline",
    "noradrnaline": "noradrenaline",
    "norad": "noradrenaline",

    "dormi": "midazolam",
    "midaz": "midazolam",

    "propof": "propofol",

    "fenta": "fentanyl",

    "kcl": "potassium",
    "potas": "potassium"
}

# -----------------------------
# SEARCH ENGINE ROBUSTE
# -----------------------------
def search_icu(query: str) -> str:

    if not query:
        return ""

    q = query.lower().strip().replace(" ", "")

    # -----------------------------
    # NORMALISATION SYNONYMES
    # -----------------------------
    for alias, real in ALIASES.items():
        if alias in q:
            q = q.replace(alias, real)

    results = []

    for drug, data in ICU_DATABASE.items():

        drug_key = drug.lower().replace(" ", "")

        # MATCH ROBUSTE
        if (
            drug_key in q
            or q in drug_key
            or drug_key[:5] in q
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
        return "non documenté dans la base ICU"

    return "\n----------------------\n".join(results)
