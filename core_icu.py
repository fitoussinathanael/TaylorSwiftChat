# =========================================================
# CORE ICU — VERSION STABLE (NO UI / NO STREAMLIT)
# =========================================================

# =========================================================
# QUICK ICU V2 — MOTEUR RÉA STABLE
# =========================================================

def quick_icu_v2(text: str):
    t = text.lower()

    # =====================================================
    # ANALYSE PAR ORGANE
    # =====================================================

    resp = 0
    hemo = 0
    infect = 0
    neuro = 0

    # RESPIRATOIRE
    if any(x in t for x in ["dysp", "hypox", "sat", "86%", "85%", "o2"]):
        resp += 2
    if "vni" in t:
        resp += 1

    # HÉMODYNAMIQUE
    if any(x in t for x in ["choc", "hypotension", "norad", "70/"]):
        hemo += 2
    if "norad" in t:
        hemo += 1

    # INFECTIEUX
    if any(x in t for x in ["fièvre", "infection", "sepsis", "pneumonie"]):
        infect += 2

    # NEURO
    if any(x in t for x in ["confusion", "coma", "glasgow", "agitation"]):
        neuro += 2

    # =====================================================
    # DOMINANCE
    # =====================================================
    organ_scores = {
        "respiratoire": resp,
        "hemodynamique": hemo,
        "infectieux": infect,
        "neurologique": neuro
    }

    dominant = max(organ_scores, key=organ_scores.get)
    max_score = organ_scores[dominant]

    # =====================================================
    # GRAVITÉ
    # =====================================================
    if max_score >= 3:
        severity = "🔴 CRITIQUE"
    elif max_score == 2:
        severity = "🟠 SÉVÈRE"
    else:
        severity = "🟡 MODÉRÉ"

    # =====================================================
    # CIBLES ICU
    # =====================================================
    targets = []

    if resp > 0:
        targets.append("🫁 SpO2 > 92%")

    if hemo > 0:
        targets.append("🫀 PAM ≥ 65 mmHg")

    if infect > 0:
        targets.append("🦠 ATB < 1h + contrôle source")

    # =====================================================
    # ACTIONS
    # =====================================================
    actions = []

    if resp >= 2:
        actions.append("🫁 Oxygène → VNI → intubation si échec")

    if hemo >= 2:
        actions.append("🫀 Remplissage + noradrénaline si hypotension")

    if infect >= 2:
        actions.append("🦠 Antibiothérapie probabiliste immédiate")

    if neuro >= 2:
        actions.append("🧠 Surveillance neurologique rapprochée")

    # =====================================================
    # ESCALADE
    # =====================================================
    escalation = []

    if resp >= 3:
        escalation.append("⚠️ risque intubation imminente")

    if hemo >= 3:
        escalation.append("⚠️ risque choc vasoplégique")

    if resp >= 2 and infect >= 2:
        escalation.append("⚠️ sepsis respiratoire probable")

    # =====================================================
    # OUTPUT
    # =====================================================
    return f"""
🧠 QUICK ICU V2 — ANALYSE RÉA

🎯 CIBLES :
{" | ".join(targets) if targets else "Surveillance clinique"}

🫀 ORGANE DOMINANT : {dominant.upper()}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS IMMÉDIATES :
{"\n".join(actions) if actions else "Surveillance + réévaluation"}

🚨 ESCALADE :
{"\n".join(escalation) if escalation else "Pas d'escalade immédiate"}

📝 INPUT :
{text}
"""


# =========================================================
# ICU FLOW V2 (SIMPLE STABLE VERSION)
# =========================================================

def build_flow(text: str):
    t = text.lower()

    resp = 2 if any(x in t for x in ["dysp", "hypox", "sat"]) else 0
    hemo = 2 if any(x in t for x in ["choc", "hypotension", "norad"]) else 0

    sofa = resp + hemo

    severity = "🔴 CRITIQUE" if sofa >= 4 else "🟠 SÉVÈRE" if sofa >= 2 else "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW

📊 RESP : {resp} | CHOC : {hemo} | SOFA : {sofa}

⚠️ GRAVITÉ : {severity}

🩺 STRATÉGIE :
- Monitorage continu
- Réévaluation clinique rapide
"""


# =========================================================
# CHECKLIST V2 (DYNAMIQUE SIMPLE CORE)
# =========================================================

def checklist_core(text: str):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    choc = any(x in t for x in ["choc", "norad", "hypotension"])
    sepsis = any(x in t for x in ["sepsis", "fièvre", "pneumonie"])

    base = ["☐ matériel", "☐ capnographie", "☐ aspiration"]

    extra = []

    if hypox:
        extra.append("🫁 préoxygénation + PEEP")

    if choc:
        extra.append("🫀 noradrénaline prête")

    if sepsis:
        extra.append("🦠 ATB probabiliste")

    return f"""
📋 CHECKLIST ICU

{" ".join(base)}

{" ".join(extra) if extra else ""}
"""
