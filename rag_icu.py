import re

# =========================================================
# BASE ICU SIMPLE MAIS ROBUSTE
# =========================================================
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

# =========================================================
# SYNONYMES ICU
# =========================================================
ALIASES = {
    "midaz": "midazolam",
    "hypnovel": "midazolam",
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrénaline": "noradrenaline",
    "fenta": "fentanyl",
    "propof": "propofol",
    "kcl": "potassium"
}

# =========================================================
# CLEAN TEXT
# =========================================================
def clean(text: str):
    return re.sub(r"[^a-zA-Z0-9 ]", "", text.lower())

# =========================================================
# SCORING ICU SIMPLE MAIS EFFICACE
# =========================================================
ICU_KEYWORDS = [
    "choc", "sepsis", "vasopresseur",
    "hypotension", "ventilation",
    "intubation", "sedation", "sédation"
]

def score_match(query, text):
    q_words = set(query.split())
    t_words = set(text.split())

    overlap = len(q_words & t_words)
    keyword_bonus = sum(1 for k in ICU_KEYWORDS if k in query)

    return overlap + keyword_bonus

# =========================================================
# RAG ICU V2
# =========================================================
def search_icu(query: str):

    if not query:
        return None

    q = clean(query)

    # alias resolution
    for alias, real in ALIASES.items():
        q = q.replace(alias, real)

    best_score = 0
    best_result = None

    for drug, data in ICU_DATABASE.items():

        blob = clean(
            drug + " " +
            data["usage"] + " " +
            data["classe"] + " " +
            data["points_icu"]
        )

        score = score_match(q, blob)

        if score > best_score:
            best_score = score
            best_result = data

    # =====================================================
    # FALLBACK INTELLIGENT (IMPORTANT)
    # =====================================================
    if best_score == 0:
        return {
            "classe": "non identifié",
            "usage": "aucun match ICU direct",
            "effets": "",
            "surveillance": "affiner la requête",
            "points_icu": "essaie: sepsis, noradrenaline, propofol, midazolam"
        }

    return best_result
