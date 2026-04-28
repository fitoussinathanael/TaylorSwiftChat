# -----------------------------
# BASE ICU (STRUCTURE STABLE)
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
        "surveillance": "TA, triglycérides, niveau sédation",
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
        "points_icu": "voie centrale recommandée, risque extravasation"
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
        "points_icu": "incompatibilité avec calcium IV"
    },

    "piperacilline": {
        "classe": "antibiotique",
        "usage": "infection nosocomiale",
        "effets": "allergie",
        "surveillance": "clinique, fonction rénale",
        "points_icu": "adapter dose insuffisance rénale"
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
# SYNONYMES / ABRÉVIATIONS
# -----------------------------
ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrnaline": "noradrenaline",

    "dormi": "midazolam",
    "midaz": "midazolam",

    "propof": "propofol",

    "fenta": "fentanyl",

    "kcl": "potassium",
    "potas": "potassium"
}

# -----------------------------
# SEARCH ENGINE STABLE
# -----------------------------
def search_icu(query: str):
    """
    Retourne une STRUCTURE DICT propre (pas du texte fragile)
    """

    if not query:
        return None

    q = query.lower().strip().replace(" ", "")

    # normalisation alias
    for alias, real in ALIASES.items():
        if alias in q:
            q = q.replace(alias, real)

    for drug, data in ICU_DATABASE.items():

        drug_key = drug.lower().replace(" ", "")

        # MATCH SIMPLE + STABLE
        if drug_key in q or q in drug_key:

            return {
                "drug": drug,
                "classe": data["classe"],
                "usage": data["usage"],
                "effets": data["effets"],
                "surveillance": data["surveillance"],
                "points_icu": data["points_icu"]
            }

    return None
