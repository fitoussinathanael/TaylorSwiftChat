# =========================================
# PHARMA HUG - IV COMPATIBILITY ENGINE
# =========================================

HUG_DB = {
    "ADRENALINE": {
        "ph": "2.5-5.0",
        "class": "vasopresseur",
        "warning": "vasopresseur critique ICU",
    },
    "NORADRENALINE": {
        "ph": None,
        "class": "vasopresseur",
        "warning": "ligne dédiée recommandée",
    },
    "AMIODARONE": {
        "ph": "3.5-4.5",
        "class": "antiarythmique",
        "warning": "incompatibilités fréquentes IV",
    },
    "MIDAZOLAM": {
        "ph": "3-4",
        "class": "benzodiazépine",
        "warning": "précipitation selon dilution",
    },
    "ACICLOVIR": {
        "ph": 11,
        "class": "antiviral",
        "warning": "risque cristallisation",
    }
}

COMPAT_RULES = [
    "Ne jamais conclure sans donnée explicite",
    "Toujours vérifier pH et concentration",
    "Perfusions critiques = ligne dédiée",
    "Acide + base = risque précipitation",
    "Nutrition parentérale = souvent incompatible"
]

def search_pharma_hug(query: str):

    if not query:
        return None

    q = query.upper().strip()

    for drug, data in HUG_DB.items():
        if drug in q:
            return {
                "drug": drug,
                **data
            }

    return None


def iv_analysis(drug: str, co_med: str = None):

    d1 = HUG_DB.get(drug.upper())

    if not d1:
        return "❌ Médicament non trouvé HUG"

    out = f"💉 PHARMA HUG — {drug.upper()}\n\n"

    out += f"Classe : {d1['class']}\n"
    out += f"pH : {d1['ph']}\n"
    out += f"⚠️ {d1['warning']}\n\n"

    if co_med:
        d2 = HUG_DB.get(co_med.upper())

        if not d2:
            out += "⚠️ Co-médicament inconnu\n"
        else:
            out += "🔬 ANALYSE MIXTURE IV\n"
            out += f"- {drug} + {co_med}\n"
            out += "→ Vérification pH / compatibilité requise\n"
            out += "→ Si doute : ligne dédiée\n"

    out += "\n📌 RÈGLES IV :\n"
    for r in COMPAT_RULES:
        out += f"- {r}\n"

    return out
