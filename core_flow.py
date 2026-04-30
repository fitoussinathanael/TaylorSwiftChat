# =========================================================
# ICU FLOW V2 — STRUCTURÉ RÉA + DOSSIER PATIENT
# =========================================================

def icu_flow_v2(text: str):
    t = text.lower()

    # =====================================================
    # SCORES ORGANIQUES
    # =====================================================
    resp = 0
    hemo = 0
    infect = 0
    neuro = 0
    metab = 0

    # =====================================================
    # RESPIRATOIRE
    # =====================================================
    if any(x in t for x in ["dysp", "hypox", "sat 86", "sat 85", "o2", "vni"]):
        resp += 2
    if "o2" in t:
        resp += 1

    # =====================================================
    # HÉMODYNAMIQUE
    # =====================================================
    if any(x in t for x in ["choc", "norad", "hypotension", "80/50"]):
        hemo += 2
    if "ta 90" in t:
        hemo += 1

    # =====================================================
    # INFECTIEUX
    # =====================================================
    if any(x in t for x in ["fièvre", "sepsis", "pneumonie", "infection"]):
        infect += 2

    # =====================================================
    # NEURO
    # =====================================================
    if any(x in t for x in ["confusion", "coma", "glasgow", "désorientation"]):
        neuro += 2

    # =====================================================
    # MÉTABOLIQUE (simple V1)
    # =====================================================
    if any(x in t for x in ["glycémie", "acidose", "lactate"]):
        metab += 1

    # =====================================================
    # CIBLES MULTIPLES (RÉA RÉEL)
    # =====================================================
    targets = []

    if resp:
        targets.append("🫁 SpO₂ > 92% / oxygénation optimale")

    if hemo:
        targets.append("🫀 PAM ≥ 65 mmHg")

    if infect:
        targets.append("🦠 ATB < 1h + contrôle source")

    if neuro:
        targets.append("🧠 Surveillance neurologique")

    if metab:
        targets.append("🧪 Correction désordres métaboliques")

    # =====================================================
    # GRAVITÉ (STABLE + NON EXAGÉRÉE)
    # =====================================================
    total = resp + hemo + infect + neuro + metab

    if hemo >= 3 or (resp >= 3 and hemo >= 2):
        severity = "🔴 CRITIQUE"

    elif total >= 4:
        severity = "🟠 SÉVÈRE"

    else:
        severity = "🟡 MODÉRÉ"

    # =====================================================
    # DIAGNOSTIC SYNTHÈSE COURTE
    # =====================================================
    summary = []

    if resp:
        summary.append("Atteinte respiratoire")

    if infect:
        summary.append("suspicion infectieuse")

    if hemo:
        summary.append("instabilité hémodynamique")

    if neuro:
        summary.append("altération neurologique")

    clinical_summary = " + ".join(summary) if summary else "stable clinique"

    # =====================================================
    # NOTE CLINIQUE (DOSSIER PATIENT)
    # =====================================================
    note = f"""
Patient évalué en urgence.

Contexte : {clinical_summary}.

Constatations :
- Respiratoire : score {resp}
- Hémodynamique : score {hemo}
- Infectieux : score {infect}
- Neurologique : score {neuro}
- Métabolique : score {metab}

Évolution à surveiller en continu.
"""

    # =====================================================
    # SBAR TRANSMISSION
    # =====================================================
    sbar = {
        "S": "Situation aiguë en cours d'évaluation",
        "B": "Contexte clinique évocateur d'atteinte multi-systèmes",
        "A": clinical_summary,
        "R": "Surveillance rapprochée + prise en charge étiologique immédiate"
    }

    # =====================================================
    # OUTPUT STRUCTURÉ FINAL
    # =====================================================
    return {
        "scores": {
            "resp": resp,
            "hemo": hemo,
            "infect": infect,
            "neuro": neuro,
            "metab": metab
        },
        "targets": targets,
        "severity": severity,
        "summary": clinical_summary,
        "note": note,
        "sbar": sbar
    }
