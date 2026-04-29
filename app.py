import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.5 PRO", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.5 PRO")
st.caption("ICU FLOW · PERFUSION MONITOR · CHECKLIST · QUICK ICU · RAG ICU")

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patients" not in st.session_state:
    st.session_state.patients = {}

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

if "dose_factor" not in st.session_state:
    st.session_state.dose_factor = 1.0

# =========================================================
# MODE
# =========================================================
mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU"]
)

# =========================================================
# CHAT HISTORY
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
# MAP
# =========================================================
def compute_map(text):
    match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not match:
        return None
    sys = int(match.group(1))
    dia = int(match.group(2))
    return round((sys + 2 * dia) / 3, 1)

# =========================================================
# ICU FLOW
# =========================================================
def build_flow(text):
    t = text.lower()

    targets = []
    if any(x in t for x in ["dysp", "hypox", "o2", "sat", "84%", "85%"]):
        targets.append("🫁 Respiratoire")
    if any(x in t for x in ["ta", "hypotension", "choc", "norad", "85/50"]):
        targets.append("🫀 Hémodynamique")
    if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]):
        targets.append("🦠 Infectieux")

    resp_score = 2 if any(x in t for x in ["hypox", "84%", "85%", "sat"]) else 0
    shock_score = 2 if any(x in t for x in ["choc", "85/50", "norad", "hypotension"]) else 0

    sofa = resp_score + shock_score

    severity = "🔴 CRITIQUE" if sofa >= 4 else "🟠 SÉVÈRE" if sofa >= 2 else "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW

🎯 CIBLES : {" | ".join(targets)}

📊 RESP : {resp_score} | CHOC : {shock_score} | SOFA : {sofa}
⚠️ GRAVITÉ : {severity}

🩺 PAM : {compute_map(text) or "N/A"} mmHg
"""

# =========================================================
# QUICK ICU (FIX IMPORTANT - FALLBACK CLINIQUE)
# =========================================================
def quick(text):
    rag = safe_rag(text)

    if rag:
        return f"""
⚡ QUICK ICU

- Classe : {rag.get('classe','-')}
- Usage : {rag.get('usage','-')}
- Effets : {rag.get('effets','-')}
- Surveillance : {rag.get('surveillance','-')}
"""

    # fallback clinique ICU (IMPORTANT)
    t = text.lower()

    resp = any(x in t for x in ["dysp", "hypox", "sat", "o2", "84%", "85%"])
    infect = any(x in t for x in ["fièvre", "pneumonie", "infection", "sepsis"])
    shock = any(x in t for x in ["choc", "hypotension", "norad", "85/50"])

    severity = "MODÉRÉ"
    if resp and infect:
        severity = "SÉVÈRE"
    if shock:
        severity = "CRITIQUE"

    return f"""
⚡ QUICK ICU (FALLBACK)

🫁 Resp : {"OUI" if resp else "NON"}
🦠 Infectieux : {"OUI" if infect else "NON"}
🫀 Choc : {"OUI" if shock else "NON"}

⚠️ Gravité : {severity}

📌 Surveillance :
- O2
- TA
- état neuro
- réévaluation rapide
"""

# =========================================================
# PERFUSION ICU MONITOR
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

ICU_LIMITS = {
    "noradrenaline": {"warn": 0.3, "crit": 1.0},
    "propofol": {"warn": 3, "crit": 5},
    "midazolam": {"warn": 0.15, "crit": 0.3}
}

def detect_perf(text):
    t = text.lower()

    drug = None
    weight = None

    for a, v in ALIASES.items():
        if a in t:
            drug = v

    w = re.findall(r'(\d{2,3})\s*(kg|k|kilo)?', t)
    if w:
        weight = int(w[0][0])

    return drug, weight

def calc(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2
    return round(((dose * weight) / conc) * 2) / 2

def perfusion_monitor(drug, weight):

    d = DRUGS[drug]
    limits = ICU_LIMITS[drug]

    st.subheader(f"💉 PERFUSION ICU — {drug.upper()}")

    factor = st.slider("Ajustement ICU (x)", 0.5, 2.0, st.session_state.dose_factor, 0.1)
    st.session_state.dose_factor = factor

    st.markdown("DOSE | IDEAL | RÉEL | STATUT")
    st.markdown("---")

    for dose in d["steps"]:

        base = calc(dose, weight, d["conc"], d["unit"])
        real = round(base * factor * 2) / 2

        if real >= limits["crit"]:
            status = "🔴 CRITIQUE"
        elif real >= limits["warn"]:
            status = "🟠 WARNING"
        else:
            status = "🟢 OK"

        st.write(f"{dose} | {base} | {real} | {status}")

        if real >= limits["crit"]:
            st.error("🚨 SURDOSAGE VASOPRESSEUR")
        elif real >= limits["warn"]:
            st.warning("⚠️ ZONE DE VIGILANCE")

# =========================================================
# CHECKLIST (ROBUSTE)
# =========================================================
def checklist(text):
    if "intubation" not in text.lower():
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    t = text.lower()

    base = """
📋 CHECKLIST INTUBATION

☐ matériel
☐ médicaments
☐ capnographie
☐ aspiration
☐ plan B
☐ équipe
"""

    if "hypox" in t or "sat" in t:
        base += "\n🫁 Pré-oxygénation renforcée"

    if "choc" in t or "norad" in t:
        base += "\n🫀 Noradrénaline prête"

    if "sepsis" in t:
        base += "\n🦠 ATB + cultures"

    return base

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = build_flow(user_input)
        st.markdown(answer)

    elif mode == "QUICK ICU":
        answer = quick(user_input)
        st.markdown(answer)

    elif mode == "PERFUSION ICU":
        drug, weight = detect_perf(user_input)

        if drug and weight:
            perfusion_monitor(drug, weight)
            answer = ""
        else:
            answer = "💉 Données manquantes (ex: noradrenaline 70 kg)"
            st.markdown(answer)

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": str(answer)})
