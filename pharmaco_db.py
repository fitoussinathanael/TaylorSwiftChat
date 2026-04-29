# =========================================================
# PHARMACO ICU DB — ICU ADULTE (RÉA + UNIVERSITAIRE CONTROLÉ)
# =========================================================

PHARMACO_DB = {

    # =====================================================
    # VASOPRESSEURS / INOTROPES
    # =====================================================
    "noradrenaline": {
        "classe": "Vasopresseur alpha1",
        "indication": "Choc septique / hypotension sévère",
        "cible": "PAM ≥ 65 mmHg",
        "dose": "0.05–1 µg/kg/min",
        "surveillance": "TA invasive, extravasation, lactate",
        "icu_score": 5
    },

    "adrenaline": {
        "classe": "Catécholamine mixte",
        "indication": "Choc réfractaire / arrêt cardiaque",
        "cible": "PAM + débit cardiaque",
        "dose": "0.05–1 µg/kg/min",
        "surveillance": "tachycardie, lactate",
        "icu_score": 5
    },

    "dobutamine": {
        "classe": "Inotrope β1",
        "indication": "Choc cardiogénique",
        "cible": "DC augmenté",
        "dose": "2–20 µg/kg/min",
        "surveillance": "tachycardie, ischémie",
        "icu_score": 4
    },

    # =====================================================
    # SÉDATION / ANALGÉSIE
    # =====================================================
    "propofol": {
        "classe": "Hypnotique IV",
        "indication": "Sédation ventilée",
        "cible": "RASS -2 à -4",
        "dose": "1–4 mg/kg/h",
        "surveillance": "hypotension, hyperTG",
        "icu_score": 4
    },

    "midazolam": {
        "classe": "Benzodiazépine",
        "indication": "Sédation prolongée",
        "cible": "RASS contrôlé",
        "dose": "0.03–0.2 mg/kg/h",
        "surveillance": "accumulation, delirium",
        "icu_score": 3
    },

    "ketamine": {
        "classe": "Anesthésique dissociatif",
        "indication": "Intubation / choc",
        "cible": "sédation + stabilité hémodynamique",
        "dose": "0.5–2 mg/kg bolus",
        "surveillance": "HTA, hallucinations",
        "icu_score": 4
    },

    # =====================================================
    # ANTIBIOTHÉRAPIE ICU (RÉA)
    # =====================================================
    "tazocilline": {
        "classe": "β-lactamine + inhibiteur",
        "indication": "Sepsis / pneumonie / abdominal",
        "cible": "ATB < 1h",
        "dose": "4g x 3–4/j",
        "surveillance": "rein, allergies",
        "icu_score": 5
    },

    "ceftriaxone": {
        "classe": "Céphalosporine 3G",
        "indication": "Pneumonie / méningite",
        "cible": "infection communautaire",
        "dose": "2g/j",
        "surveillance": "biliaire, allergie",
        "icu_score": 4
    },

    "meropenem": {
        "classe": "Carbapénème",
        "indication": "Sepsis sévère / BMR",
        "cible": "infection sévère",
        "dose": "1g x 3/j",
        "surveillance": "épilepsie, rein",
        "icu_score": 5
    },

    # =====================================================
    # AUTRES ICU
    # =====================================================
    "furosémide": {
        "classe": "Diurétique de l’anse",
        "indication": "OAP / surcharge",
        "cible": "diurèse",
        "dose": "20–80 mg",
        "surveillance": "K+, TA",
        "icu_score": 3
    }
}


# =========================================================
# HELPERS
# =========================================================
def get_drug(name: str):
    if not name:
        return None
    return PHARMACO_DB.get(name.lower())


def search_drugs(keyword: str):
    """fallback ICU simple si RAG vide"""
    keyword = keyword.lower()
    return {
        k: v for k, v in PHARMACO_DB.items()
        if keyword in k or keyword in v["indication"].lower()
    }
