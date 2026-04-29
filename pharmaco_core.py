# =========================================================
# PHARMACO CORE ICU — VERSION V2 (COMPLÈTE TERRAIN)
# =========================================================

DRUG_DB = {

# =========================================================
# 🫀 VASOPRESSEURS / INOTROPES
# =========================================================

"noradrenaline": {
    "alias": ["norad", "nora", "norepinephrine"],
    "classe": "vasopresseur",
    "unit": "µg/kg/min",
    "conc_default": 0.08,
    "steps": [0.05, 0.1, 0.2, 0.5],
    "max": 3
},

"adrenaline": {
    "alias": ["epinephrine"],
    "classe": "vasopresseur",
    "unit": "µg/kg/min",
    "conc_default": 0.1,
    "steps": [0.05, 0.1, 0.2, 0.5],
    "max": 2
},

"dobutamine": {
    "alias": ["dobu"],
    "classe": "inotrope",
    "unit": "µg/kg/min",
    "conc_default": 250,
    "steps": [2, 5, 10],
    "max": 20
},

"dopamine": {
    "alias": [],
    "classe": "inotrope",
    "unit": "µg/kg/min",
    "conc_default": 200,
    "steps": [2, 5, 10],
    "max": 20
},

"vasopressine": {
    "alias": ["vaso"],
    "classe": "vasopresseur",
    "unit": "UI/min",
    "dose_standard": "0.03 UI/min"
},

# =========================================================
# 😴 SEDATION / ANALGESIE
# =========================================================

"propofol": {
    "alias": [],
    "classe": "sédatif",
    "unit": "mg/kg/h",
    "conc_default": 10,
    "steps": [1, 2, 3, 4],
    "max": 5
},

"midazolam": {
    "alias": ["hypnovel"],
    "classe": "benzodiazépine",
    "unit": "mg/kg/h",
    "conc_default": 1,
    "steps": [0.05, 0.1, 0.2],
    "max": 0.3
},

"ketamine": {
    "alias": ["keta"],
    "classe": "anesthésique",
    "unit": "mg/kg/h",
    "conc_default": 50,
    "steps": [0.5, 1, 2],
    "max": 5
},

"fentanyl": {
    "alias": ["fenta"],
    "classe": "opioïde",
    "unit": "µg/kg/h",
    "conc_default": 50,
    "steps": [1, 2, 3],
    "max": 5
},

"sufentanil": {
    "alias": ["sufenta"],
    "classe": "opioïde",
    "unit": "µg/kg/h",
    "conc_default": 5,
    "steps": [0.1, 0.3, 0.5],
    "max": 1
},

"morphine": {
    "alias": [],
    "classe": "opioïde",
    "unit": "mg/h",
    "dose_standard": "2-10 mg/h"
},

# =========================================================
# 💪 CURARES
# =========================================================

"rocuronium": {
    "alias": ["rocu"],
    "classe": "curare",
    "dose_standard": "0.6-1 mg/kg IV"
},

"cisatracurium": {
    "alias": ["cisatra"],
    "classe": "curare",
    "unit": "mg/kg/h",
    "conc_default": 2,
    "steps": [1, 2, 3]
},

"suxamethonium": {
    "alias": ["succinylcholine"],
    "classe": "curare",
    "dose_standard": "1 mg/kg IV"
},

# =========================================================
# 🦠 ANTIBIOTIQUES
# =========================================================

"piperacilline_tazobactam": {
    "alias": ["taz", "tazocilline", "pip-tazo"],
    "classe": "antibiotique",
    "dose_standard": "4g x 3-4/j IV"
},

"ceftriaxone": {
    "alias": ["rocephine"],
    "classe": "antibiotique",
    "dose_standard": "1-2g/j"
},

"cefotaxime": {
    "alias": ["claforan"],
    "classe": "antibiotique",
    "dose_standard": "1g x 3/j"
},

"meropenem": {
    "alias": ["mero"],
    "classe": "antibiotique",
    "dose_standard": "1g x 3/j"
},

"imipenem": {
    "alias": [],
    "classe": "antibiotique",
    "dose_standard": "500mg x 4/j"
},

"amoxicilline": {
    "alias": ["amox"],
    "classe": "antibiotique",
    "dose_standard": "1g x 3/j"
},

"augmentin": {
    "alias": ["amox-clav"],
    "classe": "antibiotique",
    "dose_standard": "1g x 3/j"
},

"vancomycine": {
    "alias": ["vanco"],
    "classe": "antibiotique",
    "dose_standard": "15-20 mg/kg"
},

"linezolide": {
    "alias": ["zyvox"],
    "classe": "antibiotique",
    "dose_standard": "600mg x 2/j"
},

"gentamicine": {
    "alias": ["genta"],
    "classe": "antibiotique",
    "dose_standard": "3-5 mg/kg/j"
},

"amikacine": {
    "alias": ["amika"],
    "classe": "antibiotique",
    "dose_standard": "15-20 mg/kg"
},

"ciprofloxacine": {
    "alias": ["cipro"],
    "classe": "antibiotique",
    "dose_standard": "400mg x 2/j"
},

# =========================================================
# ❤️ CARDIO / URGENCE
# =========================================================

"amiodarone": {
    "alias": ["cordarone"],
    "classe": "antiarythmique",
    "dose_standard": "300mg IV"
},

"lidocaine": {
    "alias": [],
    "classe": "antiarythmique",
    "dose_standard": "1 mg/kg IV"
},

"atropine": {
    "alias": [],
    "classe": "anticholinergique",
    "dose_standard": "0.5 mg IV"
},

"adenosine": {
    "alias": [],
    "classe": "antiarythmique",
    "dose_standard": "6 mg IV"
},

# =========================================================
# 🧪 ANTICOAGULATION
# =========================================================

"heparine": {
    "alias": [],
    "classe": "anticoagulant",
    "dose_standard": "selon protocole"
},

"enoxaparine": {
    "alias": ["lovenox"],
    "classe": "HBPM",
    "dose_standard": "0.5-1 mg/kg"
},

# =========================================================
# ⚡ URGENCES METABOLIQUES
# =========================================================

"glucose": {
    "alias": ["g5", "g10"],
    "classe": "sucre",
    "dose_standard": "selon glycémie"
},

"insuline": {
    "alias": [],
    "classe": "hormone",
    "dose_standard": "selon protocole"
},

"bicarbonate": {
    "alias": ["bicar"],
    "classe": "tampon",
    "dose_standard": "selon GDS"
},

"calcium": {
    "alias": ["gluconate"],
    "classe": "électrolyte",
    "dose_standard": "1 amp IV"
},

"magnesium": {
    "alias": ["mg"],
    "classe": "électrolyte",
    "dose_standard": "2g IV"
}

}

# =========================================================
# 🔍 RECHERCHE ROBUSTE
# =========================================================

def find_drug(query):
    if not query:
        return None, None

    q = query.lower()

    for name, data in DRUG_DB.items():

        if name in q:
            return name, data

        for alias in data.get("alias", []):
            if alias in q:
                return name, data

    return None, None


# =========================================================
# 💉 PERFUSABLE ?
# =========================================================

def is_perfusible(data):
    return "steps" in data and "conc_default" in data


# =========================================================
# 🚨 FALLBACK
# =========================================================

def fallback_message(name):
    return f"""
❌ Médicament non référencé : {name}

👉 Vérifier protocole local
"""
