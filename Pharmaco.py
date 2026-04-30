# =========================================================
# PHARMACO ICU — VERSION ÉTENDUE RÉA (V2)
# Inspiré pratiques FRANCE / HUG
# =========================================================

DRUGS = {

    # =====================================================
    # VASOPRESSEURS / INOTROPES
    # =====================================================
    "noradrenaline": {
        "classe": "vasopresseur alpha1",
        "indication": "choc septique",
        "cible": "PAM ≥ 65 mmHg",
        "unit": "µg/kg/min",
        "conc": 0.08,
        "dose": [0.05, 0.1, 0.2, 0.5, 1],
        "max": 2
    },

    "adrenaline": {
        "classe": "vasopresseur mixte",
        "indication": "choc anaphylactique / arrêt",
        "cible": "PAM",
        "unit": "µg/kg/min",
        "conc": 0.1,
        "dose": [0.05, 0.1, 0.2, 0.5],
        "max": 2
    },

    "dobutamine": {
        "classe": "inotrope",
        "indication": "choc cardiogénique",
        "cible": "débit cardiaque",
        "unit": "µg/kg/min",
        "conc": 0.25,
        "dose": [2, 5, 10, 15],
        "max": 20
    },

    "dopamine": {
        "classe": "inotrope/vasopresseur",
        "indication": "choc (ancien usage)",
        "cible": "PAM",
        "unit": "µg/kg/min",
        "conc": 0.2,
        "dose": [2, 5, 10],
        "max": 20
    },

    # =====================================================
    # SÉDATION / ANALGÉSIE
    # =====================================================
    "propofol": {
        "classe": "sédatif",
        "indication": "sédation ventilation",
        "cible": "RASS",
        "unit": "mg/kg/h",
        "conc": 10,
        "dose": [1, 2, 3, 4],
        "max": 5
    },

    "midazolam": {
        "classe": "benzodiazépine",
        "indication": "sédation",
        "cible": "RASS",
        "unit": "mg/kg/h",
        "conc": 1,
        "dose": [0.05, 0.1, 0.2],
        "max": 0.3
    },

    "fentanyl": {
        "classe": "opioïde",
        "indication": "analgésie",
        "cible": "douleur",
        "unit": "µg/kg/h",
        "conc": 0.05,
        "dose": [1, 2, 3],
        "max": 5
    },

    "sufentanil": {
        "classe": "opioïde puissant",
        "indication": "analgésie réa",
        "cible": "douleur",
        "unit": "µg/kg/h",
        "conc": 0.01,
        "dose": [0.1, 0.2, 0.5],
        "max": 1
    },

    "ketamine": {
        "classe": "anesthésique",
        "indication": "induction / sédation",
        "cible": "analgésie + sédation",
        "unit": "mg/kg/h",
        "conc": 10,
        "dose": [0.5, 1, 2],
        "max": 3
    },

    # =====================================================
    # ANTIBIOTIQUES (MAJEURS RÉA)
    # =====================================================
    "tazocilline": {
        "classe": "ATB large spectre",
        "indication": "sepsis, pneumonie",
        "cible": "ATB < 1h",
        "unit": "g",
        "dose": [4],
        "max": 16
    },

    "ceftriaxone": {
        "classe": "céphalosporine",
        "indication": "infection sévère",
        "cible": "ATB probabiliste",
        "unit": "g",
        "dose": [1, 2],
        "max": 4
    },

    "meropenem": {
        "classe": "carbapénème",
        "indication": "sepsis grave",
        "cible": "ATB large spectre",
        "unit": "g",
        "dose": [1, 2],
        "max": 6
    },

    "vancomycine": {
        "classe": "glycopeptide",
        "indication": "infection gram+",
        "cible": "taux résiduel",
        "unit": "mg/kg",
        "dose": [15, 20],
        "max": 30
    },

    # =====================================================
    # ANTICOAGULATION
    # =====================================================
    "heparine": {
        "classe": "anticoagulant",
        "indication": "TVP / EP",
        "cible": "anti-Xa",
        "unit": "UI/kg/h",
        "dose": [10, 15, 20],
        "max": 30
    },

    "enoxaparine": {
        "classe": "HBPM",
        "indication": "prévention TVP",
        "cible": "anti-Xa",
        "unit": "mg",
        "dose": [40],
        "max": 100
    },

    # =====================================================
    # URGENCES VITALES
    # =====================================================
    "atropine": {
        "classe": "anticholinergique",
        "indication": "bradycardie",
        "cible": "FC",
        "unit": "mg",
        "dose": [0.5, 1],
        "max": 3
    },

    "amiodarone": {
        "classe": "antiarythmique",
        "indication": "troubles du rythme",
        "cible": "rythme",
        "unit": "mg",
        "dose": [150, 300],
        "max": 900
    },

    "magnesium": {
        "classe": "électrolyte",
        "indication": "torsades de pointes",
        "cible": "rythme",
        "unit": "g",
        "dose": [2],
        "max": 4
    }
}

# =========================================================
# ALIASES ROBUSTES
# =========================================================
ALIASES = {
    "norad": "noradrenaline",
    "nora": "noradrenaline",
    "adré": "adrenaline",
    "dobu": "dobutamine",
    "dopamine": "dopamine",
    "propofol": "propofol",
    "midazolam": "midazolam",
    "fenta": "fentanyl",
    "sufenta": "sufentanil",
    "keta": "ketamine",
    "taz": "tazocilline",
    "tazo": "tazocilline",
    "rocephine": "ceftriaxone",
    "mero": "meropenem",
    "vanco": "vancomycine",
    "hep": "heparine"
}


def detect_drug(text):
    t = text.lower()

    for key, val in ALIASES.items():
        if key in t:
            return val

    for drug in DRUGS:
        if drug in t:
            return drug

    return None


def get_drug(name):
    return DRUGS.get(name, None)
