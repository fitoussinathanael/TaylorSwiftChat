ICU_DATABASE = {

    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU, agitation, intubation",
        "effets": "dépression respiratoire, hypotension",
        "surveillance": "TA, FR, RASS",
        "points_icu": "accumulation en perfusion prolongée, sevrage possible"
    },

    "propofol": {
        "classe": "hypnotique IV",
        "usage": "sédation patient ventilé",
        "effets": "hypotension, bradycardie",
        "surveillance": "TA, TG, sédation",
        "points_icu": "risque syndrome perfusion propofol"
    },

    "fentanyl": {
        "classe": "opioïde",
        "usage": "analgésie en réanimation",
        "effets": "dépression respiratoire, bradycardie",
        "surveillance": "FR, douleur, sédation",
        "points_icu": "accumulation possible"
    },

    "morphine": {
        "classe": "opioïde",
        "usage": "analgésie",
        "effets": "dépression respiratoire, hypotension",
        "surveillance": "FR, douleur, conscience",
        "points_icu": "attention insuffisance rénale"
    },

    "noradrenaline": {
        "classe": "vasopresseur",
        "usage": "choc septique, hypotension",
        "effets": "vasoconstriction",
        "surveillance": "TA invasive",
        "points_icu": "voie centrale recommandée, extravasation"
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
        "points_icu": "ne pas associer calcium IV"
    },

    "piperacilline": {
        "classe": "antibiotique",
        "usage": "infection nosocomiale",
        "effets": "allergie",
        "surveillance": "clinique",
        "points_icu": "adapter fonction rénale"
    },

    "potassium": {
        "classe": "électrolyte",
        "usage": "hypokaliémie",
        "effets": "troubles du rythme",
        "surveillance": "ECG, kaliémie",
        "points_icu": "perf lente, voie sécurisée"
    },

    "calcium": {
        "classe": "électrolyte",
        "usage": "hypocalcémie",
        "effets": "arythmie",
        "surveillance": "ECG, calcémie",
        "points_icu": "attention incompatibilité ceftriaxone"
    }
}

def search_icu(query: str) -> str:

    print("DEBUG RAG INPUT:", query)

    if not query:
        return ""

    q = query.lower().strip()

    print("DEBUG NORMALIZED:", q)

    results = []

    for drug, data in ICU_DATABASE.items():

        print("CHECK DRUG:", drug)

        if drug.lower() in q or q in drug.lower():

            print("MATCH FOUND:", drug)

            results.append(f"""
MÉDICAMENT : {drug}

Classe : {data['classe']}
Usage : {data['usage']}
Effets : {data['effets']}
Surveillance : {data['surveillance']}
Points ICU : {data['points_icu']}
""")

    print("RESULTS:", results)

    return "\n".join(results)
