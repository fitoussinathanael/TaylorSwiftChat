# =========================================================
# CORE ICU V3 — STABLE RÉANIMATION LOGIQUE
# (NO UI / NO STREAMLIT / NO RAG CRITICAL DEPENDENCY)
# =========================================================

# =========================================================
# QUICK ICU V3 — MOTEUR PRINCIPAL
# =========================================================

def quick_icu_v3(text: str):
    t = text.lower()

    # =====================================================
    # INIT ORGANS
    # =====================================================
    resp = 0
    hemo = 0
    infect = 0
    neuro = 0

    # =====================================================
    # RESPIRATOIRE
    # =====================================================
    if any(x in t for x in ["dysp", "hypox", "sat 85", "sat 86", "vni", "o2"]):
        resp += 2
    if "o2" in t:
        resp += 1

    # =====================================================
    # HÉMODYNAMIQUE
    # =====================================================
    if any(x in t for x in ["norad", "choc", "80/50", "70/", "hypotension"]):
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
    # DOMINANT ORGANE
    # =====================================================
    scores = {
        "respiratoire": resp,
        "hemodynamique": hemo,
        "infectieux": infect,
        "neurologique": neuro
    }

    dominant = max(scores, key=scores.get)
    max_score = scores[dominant]

    # =====================================================
    # GRAVITÉ (LOGIQUE RÉA RÉELLE)
    # =====================================================

    # 🔴 CRITIQUE = défaillance vitale majeure
    if hemo >= 3 or resp >= 3:
        severity = "🔴 CRITIQUE"

    # 🟠 SÉVÈRE = atteinte significative multi-organe ou mono sévère
    elif (resp >= 2 and infect >= 2) or resp >= 2 or hemo >= 2:
        severity = "🟠 SÉVÈRE"

    # 🟡 MODÉRÉ
    else:
        severity = "🟡 MODÉRÉ"

    # =====================================================
    # CIBLES THÉRAPEUTIQUES
    # =====================================================
    targets = []

    if resp > 0:
        targets.append("🫁 SpO2 > 92%")

    if hemo > 0:
        targets.append("🫀 PAM ≥ 65 mmHg")

    if infect > 0:
        targets.append("🦠 ATB < 1h + contrôle source")

    if neuro > 0:
        targets.append("🧠 Surveillance neurologique")

    # =====================================================
    # ACTIONS IMMÉDIATES
    # =====================================================
    actions = []

    if resp >= 2:
        actions.append("🫁 O2 → VNI → intubation si échec")

    if hemo >= 2:
        actions.append("🫀 remplissage + vasopresseur si besoin")

    if infect >= 2:
        actions.append("🦠 ATB probabiliste immédiate")

    if neuro >= 2:
        actions.append("🧠 monitoring neuro rapproché")

    # =====================================================
    # ESCALADE
    # =====================================================
    escalation = []

    if resp >= 3:
        escalation.append("⚠️ risque intubation imminente")

    if hemo >= 3:
        escalation.append("⚠️ choc vasoplégique probable")

    if resp >= 2 and infect >= 2:
        escalation.append("⚠️ sepsis respiratoire probable")

    # =====================================================
    # OUTPUT FINAL STRUCTURÉ
    # =====================================================
    return f"""
🧠 QUICK ICU V3 — ANALYSE RÉA

🎯 CIBLES :
{" | ".join(targets) if targets else "Surveillance clinique"}

🫀 ORGANE DOMINANT : {dominant.upper()}

📊 SCORES :
Resp : {resp} | Hemo : {hemo} | Infect : {infect} | Neuro : {neuro}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS :
{"\n".join(actions) if actions else "Surveillance + réévaluation"}

🚨 ESCALADE :
{"\n".join(escalation) if escalation else "Pas d'escalade immédiate"}

📝 INPUT :
{text}
"""


# =========================================================
# FLOW ICU V2 STABLE
# =========================================================

def build_flow(text: str):
    t = text.lower()

    resp = 2 if any(x in t for x in ["dysp", "hypox", "sat"]) else 0
    hemo = 2 if any(x in t for x in ["choc", "norad", "hypotension"]) else 0
    infect = 2 if any(x in t for x in ["fièvre", "sepsis", "pneumonie"]) else 0

    sofa = resp + hemo + infect

    if sofa >= 4:
        severity = "🔴 CRITIQUE"
    elif sofa >= 2:
        severity = "🟠 SÉVÈRE"
    else:
        severity = "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW V2

📊 RESP : {resp} | HEMO : {hemo} | INFECT : {infect} | SOFA : {sofa}

⚠️ GRAVITÉ : {severity}

🧠 STRATÉGIE :
- surveillance continue
- réévaluation rapide
"""


# =========================================================
# CHECKLIST ICU DYNAMIQUE V2
# =========================================================

def checklist_core(text: str):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    choc = any(x in t for x in ["choc", "norad", "hypotension"])
    sepsis = any(x in t for x in ["sepsis", "fièvre", "pneumonie"])

    base = [
        "☐ matériel prêt",
        "☐ aspiration fonctionnelle",
        "☐ capnographie opérationnelle"
    ]

    extra = []

    if hypox:
        extra.append("🫁 préoxygénation + PEEP")

    if choc:
        extra.append("🫀 noradrénaline prête")

    if sepsis:
        extra.append("🦠 ATB probabiliste immédiate")

    return f"""
📋 CHECKLIST ICU DYNAMIQUE

{" ".join(base)}

{" ".join(extra) if extra else ""}
"""
