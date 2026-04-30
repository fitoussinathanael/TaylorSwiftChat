# =========================================================
# ICU ASSIST V1 — RÉDUCTION CHARGE COGNITIVE
# FLOW → ACTIONS CLINIQUES PRIORITAIRES
# =========================================================

from pharmaco import detect_drug, get_drug


def icu_assist(text, flow, pharmaco=None):

    urgency = flow.get("severity", "🟡 MODÉRÉ")
    scores = flow.get("scores", {})

    actions = []
    warnings = []
    pharmaco_flags = []

    # =====================================================
    # RESPIRATOIRE
    # =====================================================
    if scores.get("resp", 0) >= 2:
        actions.append("🫁 Oxygène / VNI / intubation si échec")
        warnings.append("Risque insuffisance respiratoire")

    # =====================================================
    # HÉMODYNAMIQUE
    # =====================================================
    if scores.get("hemo", 0) >= 2:
        actions.append("🫀 Remplissage + vasopresseur probable")

        drug = detect_drug(text)
        if drug:
            drug_data = get_drug(drug)
            if drug_data:
                pharmaco_flags.append(f"💉 Perfusion active détectée : {drug}")
                actions.append(f"Adapter perfusion : {drug}")

    # =====================================================
    # INFECTIEUX
    # =====================================================
    if scores.get("infect", 0) >= 2:
        actions.append("🦠 ATB probabiliste < 1h")
        warnings.append("Suspicion sepsis / infection sévère")

    # =====================================================
    # NEUROLOGIQUE
    # =====================================================
    if scores.get("neuro", 0) >= 2:
        actions.append("🧠 Surveillance neurologique rapprochée")
        warnings.append("Altération neurologique possible")

    # =====================================================
    # MÉTABOLIQUE
    # =====================================================
    if scores.get("metab", 0) >= 1:
        actions.append("🧪 Correction désordres métaboliques")

    # =====================================================
    # PRIORISATION SIMPLE (SÉCURITÉ INFIRMIÈRE)
    # =====================================================
    if urgency == "🔴 CRITIQUE":
        priority = "🔴 ACTION IMMÉDIATE"
    elif urgency == "🟠 SÉVÈRE":
        priority = "🟠 SURVEILLANCE ACTIVE"
    else:
        priority = "🟡 STABLE / SURVEILLANCE"

    # =====================================================
    # SUMMARY ULTRA COURT
    # =====================================================
    summary = flow.get("summary", "stable clinique")

    # =====================================================
    # SBAR SIMPLIFIÉ
    # =====================================================
    sbar = flow.get("sbar", {
        "S": "Situation en cours",
        "B": "Contexte clinique",
        "A": summary,
        "R": "Surveillance + prise en charge adaptée"
    })

    # =====================================================
    # OUTPUT FINAL
    # =====================================================
    return {
        "priority": priority,
        "urgency": urgency,
        "summary": summary,
        "actions": actions,
        "warnings": warnings,
        "pharmaco_flags": pharmaco_flags,
        "safety_note": "Surveillance continue recommandée en environnement critique",
        "sbar": sbar
    }
