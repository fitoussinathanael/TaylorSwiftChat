ICU_DATABASE = {
    "midazolam": {
        "classe": "benzodiazépine",
        "usage": "sédation ICU",
        "effets": "dépression respiratoire",
        "surveillance": "TA, FR, RASS",
        "points_icu": "accumulation"
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
