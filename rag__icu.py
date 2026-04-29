import re

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
    "hypnovel": "midazolam",
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "kcl": "potassium",
    "fenta": "fentanyl",
    "propof": "propofol"
}

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    return re.sub(r"[^a-zA-Z0-9 ]", "", text.lower())

# -----------------------------
# SCORE MATCH ICU
# -----------------------------
def score_match(query, text):
    q_words = set(query.split())
    t_words = set(text.split())

    # overlap lexical
    overlap = len(q_words & t_words)

    # bonus mots clés ICU
    ICU_KEYWORDS = [
        "choc", "sepsis", "vasopresseur",
        "ventilation", "sédation", "hypotension",
        "intubation", "ICU", "réanimation"
    ]

    keyword_bonus = sum(1 for w in ICU_KEYWORDS if w in query)

    return overlap + keyword_bonus

# -----------------------------
# SEARCH ICU V2
# -----------------------------
def search_icu(query: str):

    if not query:
        return None

    query = clean(query)

    # alias resolution
    for alias, real in ALIASES.items():
        query = query.replace(alias, real)

    best_score = 0
    best_match = None

    for drug, data in ICU_DATABASE.items():

        text_blob = clean(
            drug + " " +
            data["usage"] + " " +
            data["classe"] + " " +
            data["points_icu"]
        )

        score = score_match(query, text_blob)

        if score > best_score:
            best_score = score
            best_match = data

    # -----------------------------
    # FALLBACK INTELLIGENT
    # -----------------------------
    if best_score == 0:
        return {
            "title": "Aucun match précis",
            "usage": "Essaye : noradrenaline, midazolam, propofol, sepsis, choc",
            "effets": "",
            "surveillance": "",
            "points_icu": "RAG amélioré : élargis la base ICU"
        }

    return best_match
