# =========================================================
# CORE ICU ENGINE — LOGIQUE CLINIQUE CENTRALISÉE
# =========================================================

from pharmaco_db import PHARMACO_DB, search_drugs


# =========================================================
# QUICK ICU — MOTEUR RÉA STRUCTURÉ
# =========================================================
def quick_icu(text: str):
    t = text.lower()

    # =========================
    # CIBLES RÉANIMATION
    # =========================
    targets = []

    if any(x in t for x in ["dysp", "hypox", "sat", "o2", "86%", "85%"]):
        targets.append("🫁 SpO2 > 92%")

    if any(x in t for x in ["ta", "hypotension", "choc", "norad", "70/"]):
        targets.append("🫀 PAM ≥ 65 mmHg")

    if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]):
        targets.append("🦠 ATB < 1h + contrôle source")

    # =========================
    # GRAVITÉ
    # =========================
    resp = 2 if any(x in t for x in ["hypox", "sat 86", "dysp"]) else 0
    shock = 2 if any(x in t for x in ["choc", "norad", "ta basse"]) else 0
    sepsis = 1 if "sepsis" in t else 0

    score = resp + shock + sepsis

    severity = (
        "🔴 CRITIQUE" if score >= 4 else
        "🟠 SÉVÈRE" if score >= 2 else
        "🟡 MODÉRÉ"
    )

    # =========================
    # ACTIONS RÉA AUTOMATIQUES
    # =========================
    actions = []

    if resp >= 2:
        actions.append("🫁 Oxygène → VNI → intubation si échec")

    if shock >= 2:
        actions.append("🫀 Remplissage + noradrénaline")

    if sepsis:
        actions.append("🦠 ATB probabiliste immédiate")

    # =========================
    # OUTPUT STRUCTURÉ
    # =========================
    return f"""
⚡ QUICK ICU — ANALYSE RÉA

🎯 CIBLES : {" | ".join(targets) if targets else "Évaluation clinique"}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS :
{"\n".join(actions) if actions else "Surveillance + évaluation"}

📝 INPUT :
{text}
"""


# =========================================================
# PERFUSION ICU — FALLBACK PHARMACO
# =========================================================
def quick_drug_info(name: str):
    drug = PHARMACO_DB.get(name.lower())

    if not drug:
        results = search_drugs(name)
        if not results:
            return "❌ Médicament non trouvé"
        drug = list(results.values())[0]

    return f"""
💉 PHARMACO ICU

📌 Classe : {drug['classe']}
📌 Indication : {drug['indication']}
🎯 Cible : {drug['cible']}
💊 Dose : {drug['dose']}
⚠️ Surveillance : {drug['surveillance']}
"""
    

# =========================================================
# CHECKLIST INTELLIGENTE
# =========================================================
def checklist_icu(text: str):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "86%", "dysp"])
    shock = any(x in t for x in ["choc", "norad", "hypotension"])
    sepsis = any(x in t for x in ["sepsis", "fièvre", "infection"])

    base = [
        "📋 CHECKLIST INTUBATION ICU",
        "☐ matériel prêt",
        "☐ aspiration fonctionnelle",
        "☐ capnographie branchée",
        "☐ médicaments préparés",
        "☐ équipe disponible",
    ]

    if hypox:
        base += [
            "",
            "🫁 HYPOXIE",
            "☐ Préoxygénation prolongée",
            "☐ PEEP prête",
            "☐ aspiration répétée",
            "⚠️ risque désaturation rapide",
        ]

    if shock:
        base += [
            "",
            "🫀 CHOC",
            "☐ Noradrénaline prête",
            "☐ voie veineuse sécurisée",
            "☐ monitoring continu TA",
            "⚠️ risque collapsus",
        ]

    if sepsis:
        base += [
            "",
            "🦠 SEPSIS",
            "☐ ATB dans l’heure",
            "☐ hémocultures si possible",
            "☐ lactates",
            "⚠️ défaillance multi-organes",
        ]

    return "\n".join(base)
