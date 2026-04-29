from pharmaco import DRUG_DATABASE

# =========================================================
# NORMALISATION TEXTE
# =========================================================
def normalize(text: str):
    return text.lower().strip()

# =========================================================
# INDEX ALIASES
# =========================================================
ALIAS_MAP = {}

for drug_name, data in DRUG_DATABASE.items():
    ALIAS_MAP[drug_name] = drug_name
    for alias in data.get("aliases", []):
        ALIAS_MAP[alias] = drug_name

# =========================================================
# FUZZY MATCH SIMPLE
# =========================================================
def fuzzy_match(query):
    for key in ALIAS_MAP:
        if key in query:
            return ALIAS_MAP[key]
    return None

# =========================================================
# SEARCH ICU
# =========================================================
def search_icu(query: str):

    if not query:
        return None

    q = normalize(query)

    # 1️⃣ match direct
    if q in DRUG_DATABASE:
        return DRUG_DATABASE[q]

    # 2️⃣ alias / fuzzy
    match = fuzzy_match(q)
    if match:
        return DRUG_DATABASE.get(match)

    # 3️⃣ fallback intelligent (critique)
    return {
        "classe": "Non trouvé",
        "usage": "Médicament non reconnu",
        "effets": "Vérifier orthographe ou base",
        "surveillance": "Aucune donnée",
        "points_icu": "⚠️ Ajouter dans pharmaco.py"
    }
