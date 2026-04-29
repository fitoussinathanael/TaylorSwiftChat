# =========================================================
# RAG ICU ENGINE V3 - CLINICAL READY (NO BREAK APP)
# =========================================================

ICU_DATABASE = {

    # ================= VASOPRESSEURS =================
    "noradrenaline": {
        "classe": "vasopresseur (alpha1 dominant)",
        "usage": "choc septique, hypotension sévère",
        "effets": "vasoconstriction, risque ischémie périphérique",
        "surveillance": "TA invasive, lactate, diurèse, extrémités",
        "points_icu": "1ère ligne choc septique - voie centrale recommandée"
    },

    "adrenaline": {
        "classe": "catécholamine mixte",
        "usage": "arrêt cardiaque, choc anaphylactique",
        "effets": "tachycardie, hyperlactatémie, HTA",
        "surveillance": "ECG, TA invasive, lactate",
        "points_icu": "réanimation avancée"
    },

    "dobutamine": {
        "classe": "inotrope beta1",
        "usage": "choc cardiogénique, bas débit",
        "effets": "tachycardie, arythmies",
        "surveillance": "ECG, débit cardiaque",
        "points_icu": "améliore contractilité"
    },

    # ================= SÉDATION =================
    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation ventilation mécanique",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, triglycérides, RASS",
        "points_icu": "risque syndrome propofol si doses élevées"
    },

    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU, agitation",
        "effets": "dépression respiratoire",
        "surveillance": "RASS, TA, FR",
        "points_icu": "accumulation prolongée"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie réanimation",
        "effets": "dépression respiratoire",
        "surveillance": "FR, douleur",
        "points_icu": "accumulation tissu gras"
    },

    "ketamine": {
        "classe": "anesthésique dissociatif",
        "usage": "induction intubation, choc",
        "effets": "HTA, hallucinations",
        "surveillance": "TA, conscience",
        "points_icu": "utile en choc hypotensif"
    },

    # ================= CURARES =================
    "rocuronium": {
        "classe": "curare non dépolarisant",
        "usage": "intubation, ventilation",
        "effets": "paralysie musculaire",
        "surveillance": "TOF",
        "points_icu": "associer sédation obligatoire"
    },

    "succinylcholine": {
        "classe": "curare dépolarisant",
        "usage": "intubation rapide",
        "effets": "hyperkaliémie",
        "surveillance": "ECG, K+",
        "points_icu": "CI brûlés / trauma / hyperK"
    },

    # ================= ELECTROLYTES =================
    "potassium": {
        "classe": "électrolyte",
        "usage": "hypokaliémie",
        "effets": "troubles rythme",
        "surveillance": "ECG, kaliémie",
        "points_icu": "administration lente obligatoire"
    },

    "magnesium": {
        "classe": "électrolyte",
        "usage": "torsades de pointe",
        "effets": "hypotension si rapide",
        "surveillance": "ECG",
        "points_icu": "anti-arythmique ventriculaire"
    }
}

# =========================================================
# SYNONYMES ROBUSTES
# =========================================================

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrénaline": "noradrenaline",

    "adré": "adrenaline",

    "dobu": "dobutamine",

    "propof": "propofol",
    "midaz": "midazolam",
    "fenta": "fentanyl",
    "keta": "ketamine",

    "roc": "rocuronium",
    "sux": "succinylcholine",

    "kcl": "potassium",
    "mg": "magnesium"
}

# =========================================================
# ICU SEARCH ENGINE V3 (ROBUST + CLINICAL CONTEXT)
# =========================================================

def search_icu(query: str):

    if not query:
        return None

    q = query.lower().strip()
    q = q.replace(" ", "")

    # ---------------- alias resolution ----------------
    for alias, real in ALIASES.items():
        if alias in q:
            q = q.replace(alias, real)

    # ---------------- drug match ----------------
    for drug, data in ICU_DATABASE.items():
        if drug in q:
            return data

    # ---------------- CLINICAL SYNDROMES ----------------

    # SEPSIS / CHOC SEPTIQUE
    if "sepsis" in q or "chocseptique" in q:

        return {
            "classe": "syndrome infectieux sévère",
            "usage": "sepsis / choc septique (urgence vitale)",
            "effets": "vasodilatation, hypoperfusion, défaillance multiviscérale",
            "surveillance": "TA, lactate, diurèse, SpO2, état mental",
            "points_icu": "ATB < 1h + remplissage + noradrénaline si hypotension"
        }

    # LACTATE
    if "lactate" in q:

        return {
            "classe": "biomarqueur de perfusion",
            "usage": "évaluation choc / hypoperfusion",
            "effets": "élévation = souffrance tissulaire",
            "surveillance": "tendance lactate (trend)",
            "points_icu": "objectif décroissance après traitement"
        }

    # VENTILATION / SDRA
    if "ventilation" in q or "sdra" in q:

        return {
            "classe": "insuffisance respiratoire aiguë",
            "usage": "SDRA / ventilation mécanique",
            "effets": "hypoxémie sévère",
            "surveillance": "SpO2, GDS, compliance",
            "points_icu": "PEEP + ventilation protectrice"
        }

    return None
