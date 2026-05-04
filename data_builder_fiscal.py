import os

BASE_PATH = "data/legal/fiscal"

# ----------------------------
# 1. LOIS
# ----------------------------
lois = [
    {
        "filename": "cgi_article_1729.txt",
        "content": """
TYPE: LOI
SOURCE: Code général des impôts
ARTICLE: 1729
DOMAINE: Sanctions fiscales

CONTENU:
Les insuffisances, inexactitudes ou omissions relevées dans une déclaration entraînent l'application de majorations lorsque le manquement est délibéré.

PORTÉE:
Base juridique des pénalités fiscales en cas de mauvaise foi.
"""
    },
    {
        "filename": "procedures_fiscales.txt",
        "content": """
TYPE: LOI
SOURCE: Livre des procédures fiscales
DOMAINE: Contrôle fiscal

CONTENU:
L'administration fiscale peut procéder à des vérifications de comptabilité et examens de situation fiscale personnelle.

PORTÉE:
Encadre les pouvoirs de contrôle de l'administration.
"""
    }
]

# ----------------------------
# 2. JURISPRUDENCE
# ----------------------------
jurisprudence = [
    {
        "filename": "ce_2022_redressement.txt",
        "content": """
TYPE: JURISPRUDENCE
JURIDICTION: Conseil d'État
DATE: 2022

FAITS:
Contestations d’un redressement fiscal sur charges déductibles.

PRINCIPE:
Le juge contrôle la réalité et la justification des charges.

PORTÉE:
Renforce l’exigence de preuve documentaire.
"""
    },
    {
        "filename": "cass_2021_abus_droit.txt",
        "content": """
TYPE: JURISPRUDENCE
JURIDICTION: Cour de cassation
DATE: 2021

PRINCIPE:
L’abus de droit est caractérisé si l’opération a un but principalement fiscal sans substance économique.

PORTÉE:
Permet la requalification des montages artificiels.
"""
    }
]

# ----------------------------
# 3. CAS PRATIQUES
# ----------------------------
cas_pratiques = [
    {
        "filename": "redressement_tva_entreprise.txt",
        "content": """
TYPE: CAS_PRATIQUE
DOMAINE: TVA entreprise

PROBLEME:
Redressement fiscal sur TVA mal ventilée entre usage pro et perso.

ANALYSE:
Absence de justificatifs précis.

SOLUTION:
Reconstitution des pièces + justification économique.

RESULTAT:
Réduction partielle du redressement.
"""
    },
    {
        "filename": "controle_fiscal_particulier.txt",
        "content": """
TYPE: CAS_PRATIQUE
DOMAINE: Particulier

PROBLEME:
Contrôle fiscal basé sur flux bancaires.

STRATEGIE:
Justification des transferts familiaux.

POINT_CLE:
Importance de la traçabilité des flux.
"""
    }
]


# ----------------------------
# 4. CREATION DES FICHIERS
# ----------------------------
def write_files(category, items):
    path = os.path.join(BASE_PATH, category)
    os.makedirs(path, exist_ok=True)

    for item in items:
        file_path = os.path.join(path, item["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(item["content"].strip())


def main():
    write_files("loi", lois)
    write_files("jurisprudence", jurisprudence)
    write_files("cas_pratiques", cas_pratiques)

    print("✅ Base juridique fiscale générée avec succès.")


if __name__ == "__main__":
    main()
