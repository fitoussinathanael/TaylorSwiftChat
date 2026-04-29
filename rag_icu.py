# =========================================================
# RAG ICU ENGINE V2 - ENRICHED CLINICAL DATABASE
# Compatible ICU ENGINE V10.3
# =========================================================

ICU_DATABASE = {

    # =====================================================
    # VASOPRESSEURS
    # =====================================================
    "noradrenaline": {
        "classe": "vasopresseur (alpha1 > beta1)",
        "usage": "choc septique, choc vasoplégique, hypotension sévère",
        "effets": "vasoconstriction, ischémie périphérique possible, tachycardie",
        "surveillance": "TA invasive, lactate, perfusion périphérique, diurèse",
        "points_icu": "1ère ligne en choc septique. voie centrale recommandée. titration continue"
    },

    "adrenaline": {
        "classe": "catécholamine mixte",
        "usage": "arrêt cardiaque, choc réfractaire, anaphylaxie",
        "effets": "tachycardie, hyperglycémie, lactate ↑",
        "surveillance": "ECG, TA invasive, lactate",
        "points_icu": "utile si échec noradrénaline"
    },

    "dobutamine": {
        "classe": "inotrope beta1",
        "usage": "choc cardiogénique, bas débit cardiaque",
        "effets": "tachycardie, arythmies",
        "surveillance": "ECG, débit cardiaque, TA",
        "points_icu": "améliore contractilité"
    },

    # =====================================================
    # SEDATION / ANALGESIE
    # =====================================================
    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation patient ventilé",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, profondeur sédation",
        "points_icu": "risque syndrome propofol (dose élevée prolongée)"
    },

    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU, agitation, intubation",
        "effets": "dépression respiratoire, hypotension",
        "surveillance": "RASS, FR, TA",
        "points_icu": "accumulation en perfusion prolongée"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie réanimation",
        "effets": "dépression respiratoire, rigidité thoracique",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation tissu graisseux"
    },

    "ketamine": {
        "classe": "anesthésique dissociatif",
        "usage": "induction intubation, choc, bronchospasme",
        "effets": "hallucinations, HTA, tachycardie",
        "surveillance": "TA, conscience",
        "points_icu": "utile en choc hypotensif"
    },

    # =====================================================
    # CURARES
    # =====================================================
    "rocuronium": {
        "classe": "curare non dépolarisant",
        "usage": "intubation rapide, ventilation contrôlée",
        "effets": "paralysie musculaire",
        "surveillance": "TOF, ventilation",
        "points_icu": "pas d'effet sédatif → associer hypnotique"
    },

    "succinylcholine": {
        "classe": "curare dépolarisant",
        "usage": "intubation rapide",
        "effets": "hyperkaliémie, bradycardie",
        "surveillance": "ECG, potassium",
        "points_icu": "CI hyperkaliémie / brûlés / trauma"
    },

    # =====================================================
    # ELECTROLYTES
    # =====================================================
    "potassium": {
        "classe": "électrolyte",
        "usage": "hypokaliémie sévère",
        "effets": "troubles du rythme",
        "surveillance": "ECG continu, kaliémie",
        "points_icu": "jamais bolus IV direct"
    },

    "magnesium": {
        "classe": "électrolyte",
        "usage": "torsades de pointe, hypomagnésémie",
        "effets": "hypotension si rapide",
        "surveillance": "ECG, magnésémie",
        "points_icu": "anti-arythmique ventriculaire"
    },

    # =====================================================
    # ANTIBIOTHERAPIE (SEPSIS CORE)
    # =====================================================
    "ceftriaxone": {
        "classe": "céphalosporine 3G",
        "usage": "sepsis communautaire, méningite",
        "effets": "diarrhée, cytolyse",
        "surveillance": "fonction hépatique",
        "points_icu": "large spectre Gram -"
    },

    "piperacilline tazobactam": {
        "classe": "bêta-lactamine large spectre",
        "usage": "sepsis sévère nosocomial",
        "effets": "allergie, atteinte rénale",
        "surveillance": "créatinine",
        "points_icu": "couverture Pseudomonas"
    },

    "vancomycine": {
        "classe": "glycopeptide",
        "usage": "MRSA",
        "effets": "néphrotoxicité",
        "surveillance": "trough levels",
        "points_icu": "adaptation posologique indispensable"
    }
}

# =========================================================
# SYNONYMES ICU (ULTRA IMPORTANT POUR TON FLOW)
# =========================================================
ALIASES = {

    # vasopresseurs
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrénaline": "noradrenaline",

    "adré": "adrenaline",

    "dobu": "dobutamine",

    # sedation
    "propof": "propofol",
    "midaz": "midazolam",
    "fenta": "fentanyl",
    "keta": "ketamine",

    # curare
    "roc": "rocuronium",
    "sux": "succinylcholine",

    # electrolytes
    "kcl": "potassium",
    "mg": "magnesium",

    # antibiotiques
    "pip tazo": "piperacilline tazobactam",
    "pip-tazo": "piperacilline tazobactam",
    "vanco": "vancomycine"
}

# =========================================================
# SEARCH ICU ENGINE (ROBUST)
# =========================================================
def search_icu(query: str):

    if not query:
        return None

    q = query.lower().strip()

    # normalisation aliases
    for alias, real in ALIASES.items():
        if alias in q:
            q = q.replace(alias, real)

    # recherche directe
    for drug, data in ICU_DATABASE.items():
        if drug in q:
            return data

    # recherche partielle inversée
    for drug, data in ICU_DATABASE.items():
        if any(word in drug for word in q.split()):
            return data

    return None
