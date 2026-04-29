import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.4 PRO", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.4 PRO")
st.caption("ICU FLOW · PERFUSION · CHECKLIST · QUICK ICU · RAG ICU")

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patients" not in st.session_state:
    st.session_state.patients = {}

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

# =========================================================
# MODE
# =========================================================
mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU"]
)

# =========================================================
# PATIENT
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {"notes": []}
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHAT
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# SAFE RAG
# =========================================================
def safe_rag(query: str):
    try:
        if not query:
            return None
        res = search_icu(query)
        return res if isinstance(res, dict) else None
    except:
        return None

# =========================================================
# PAM
# =========================================================
def compute_map(text):
    match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not match:
        return None
    sys = int(match.group(1))
    dia = int(match.group(2))
    return round((sys + 2 * dia) / 3, 1)

# =========================================================
# ICU FLOW (VERSION ENHANCED SAFE)
# =========================================================
def build_flow(text):
    t = text.lower()

    # -------------------------
    # CIBLES
    # -------------------------
    targets = []
    if any(x in t for x in ["dysp", "hypox", "o2", "sat", "84%", "85%"]):
        targets.append("🫁 Respiratoire")
    if any(x in t for x in ["ta", "hypotension", "choc", "norad", "85/50"]):
        targets.append("🫀 Hémodynamique")
    if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]):
        targets.append("🦠 Infectieux")

    # -------------------------
    # SCORE RESP
    # -------------------------
    resp_score = 0
    if "dysp" in t:
        resp_score += 1
    if "hypox" in t or "84%" in t or "85%" in t:
        resp_score += 2
    if "o2" in t or "sat" in t:
        resp_score += 1

    # -------------------------
    # SCORE CHOC (RENFORCÉ ICU)
    # -------------------------
    shock_score = 0
    if "ta" in t or "85/50" in t or "hypotension" in t:
        shock_score += 2
    if "choc" in t:
        shock_score += 2
    if "norad" in t:
        shock_score += 2
    if "confusion" in t:
        shock_score += 1
    if "fièvre" in t or "sepsis" in t:
        shock_score += 1

    # -------------------------
    # SOFA LIGHT (SIMPLE ICU)
    # -------------------------
    sofa = 0
    if resp_score >= 2:
        sofa += 2
    if shock_score >= 2:
        sofa += 2
    if "confusion" in t:
        sofa += 1

    # -------------------------
    # GRAVITÉ
    # -------------------------
    total = resp_score + shock_score

    if total >= 5 or sofa >= 4:
        severity = "🔴 CRITIQUE"
    elif total >= 3:
        severity = "🟠 SÉVÈRE"
    elif total >= 1:
        severity = "🟡 MODÉRÉ"
    else:
        severity = "🟢 STABLE"

    # -------------------------
    # OVERRIDE ICU (IMPORTANT)
    # -------------------------
    if "84%" in t or "85%" in t or "85/50" in t:
        severity = "🔴 CRITIQUE"

    # -------------------------
    # ASSESSMENT
    # -------------------------
    if "hypox" in t or "84%" in t or "85%" in t:
        assessment = "Hypoxémie significative → insuffisance respiratoire aiguë probable"
    elif "sepsis" in t or "fièvre" in t:
        assessment = "Suspicion sepsis → risque choc septique évolutif"
    elif "oap" in t:
        assessment = "Suspicion OAP → origine cardiogénique probable"
    else:
        assessment = "Atteinte aiguë en cours d’évaluation"

    # -------------------------
    # PAM
    # -------------------------
    pam = compute_map(text)
    pam_line = f"🩺 PAM : {pam} mmHg\n" if pam else ""

    # -------------------------
    # ALERTES
    # -------------------------
    alerts = []

    if resp_score >= 2:
        alerts.append("🫁 ALERTE RESPIRATOIRE")

    if shock_score >= 2:
        alerts.append("🫀 ALERTE CHOC")

    if resp_score >= 2 and shock_score >= 2:
        alerts.append("🚨 RISQUE MULTI-ORGANE (SEPSIS PROBABLE)")

    if severity == "🔴 CRITIQUE":
        alerts.append("🚨 RISQUE INTUBATION / RÉANIMATION")

    # -------------------------
    # SBAR
    # -------------------------
    sbar = f"""
🧾 TRANSMISSION (SBAR)

S - Situation :
{text}

B - Background :
Patient en contexte aigu nécessitant surveillance rapprochée

A - Assessment :
{assessment}
{pam_line}

R - Recommendation :
Monitorage continu
Réévaluation clinique rapide
Adaptation thérapeutique selon évolution
"""

    # -------------------------
    # OUTPUT
    # -------------------------
    out = "🧠 ICU FLOW STRUCTURÉ\n\n"

    out += "🎯 CIBLES : " + " | ".join(targets) + "\n\n"
    out += f"📊 SCORE RESP : {resp_score} | SCORE CHOC : {shock_score} | SOFA-L : {sofa}\n"
    out += f"⚠️ GRAVITÉ : {severity}\n\n"

    if alerts:
        out += "🚨 ALERTES :\n" + "\n".join(alerts) + "\n\n"

    out += "🧠 ASSESSMENT :\n" + assessment + "\n\n"
    out += sbar

    return out

# =========================================================
# QUICK ICU
# =========================================================
def quick(text):
    rag = safe_rag(text)

    if not rag:
        return "⚡ QUICK ICU\n\n❌ Aucun résultat RAG."

    return (
        "⚡ QUICK ICU\n\n"
        f"- Classe : {rag.get('classe','-')}\n"
        f"- Usage : {rag.get('usage','-')}\n"
        f"- Effets : {rag.get('effets','-')}\n"
        f"- Surveillance : {rag.get('surveillance','-')}\n"
        f"- Points ICU : {rag.get('points_icu','-')}\n"
    )

# =========================================================
# PERFUSION ICU (STABLE)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "steps": [1, 2, 3, 4]},
    "midazolam": {"conc": 1, "unit": "mg/kg/h", "steps": [0.05, 0.1, 0.2]}
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrenaline": "noradrenaline",
    "propofol": "propofol",
    "midazolam": "midazolam"
}

def detect_perf(text):
    t = text.lower()
    drug = None
    weight = None

    for a, v in ALIASES.items():
        if a in t:
            drug = v

    w = re.findall(r'(\d{2,3})\s*kg', t)
    if w:
        weight = int(w[0])

    return drug, weight

def calc(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        exact = (dose * weight * 60) / (conc * 1000)
    else:
        exact = (dose * weight) / conc

    ide = round(exact * 2) / 2
    return ide, exact

def perfusion(drug, weight):
    d = DRUGS[drug]

    out = f"💉 {drug.upper()} — {weight} kg\n\n"
    out += "| Dose | IDE | Exact |\n|---|---|---|\n"

    for dose in d["steps"]:
        ide, exact = calc(dose, weight, d["conc"], d["unit"])
        out += f"| {dose} | {ide:.1f} | ({exact:.2f}) |\n"

    rag = safe_rag(drug)
    if rag:
        out += "\n📖 RAG ICU\n"
        out += f"- {rag.get('classe','')}\n- {rag.get('usage','')}\n"

    return out

# =========================================================
# CHECKLIST
# =========================================================
def checklist(text):
    return "📋 CHECKLIST INTUBATION\n☐ matériel ☐ médicaments ☐ vérifications"

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = build_flow(user_input)

    elif mode == "QUICK ICU":
        answer = quick(user_input)

    elif mode == "PERFUSION ICU":
        drug, weight = detect_perf(user_input)
        answer = perfusion(drug, weight) if drug and weight else "💉 Données manquantes"

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
