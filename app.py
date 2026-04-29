import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.6 PRO", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.6 PRO")
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
# ICU FLOW (STABLE)
# =========================================================
def build_flow(text):
    t = text.lower()

    targets = []
    if any(x in t for x in ["dysp", "hypox", "sat", "84", "85"]):
        targets.append("🫁 Respiratoire")
    if any(x in t for x in ["ta", "hypotension", "choc", "norad"]):
        targets.append("🫀 Hémodynamique")
    if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]):
        targets.append("🦠 Infectieux")

    resp = 2 if any(x in t for x in ["hypox", "84", "85", "sat"]) else 0
    shock = 2 if any(x in t for x in ["choc", "norad", "85/50"]) else 0

    sofa = resp + shock
    severity = "🔴 CRITIQUE" if sofa >= 4 else "🟠 SÉVÈRE" if sofa >= 2 else "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW (ABCDE)

🎯 CIBLES : {" | ".join(targets)}

📊 RESP : {resp} | CHOC : {shock} | SOFA : {sofa}
⚠️ GRAVITÉ : {severity}

🩺 PAM : {compute_map(text) or "N/A"} mmHg

🧠 PRIORITÉS :
A - Airway sécurisé
B - Oxygenation / VNI si échec
C - Perfusion / vasopresseurs si choc
D - État neurologique
E - Infection / sepsis
"""

# =========================================================
# QUICK ICU (CORRIGÉ RÉA STRUCTURÉ)
# =========================================================
def quick(text):
    t = text.lower()

    resp = "🫁 SpO2 > 92% / optimisation oxygénation"
    hemo = "🫀 PAM ≥ 65 mmHg"
    inf = "🦠 ATB < 1h + contrôle source"

    severity = "🟡 MODÉRÉ"
    actions = []

    if "sat" in t or "hypox" in t or "dysp" in t:
        severity = "🟠 SÉVÈRE"
        actions.append("Oxygène → VNI → intubation si échec")

    if "choc" in t or "norad" in t or "85/50" in t:
        severity = "🔴 CRITIQUE"
        actions.append("Remplissage + noradrénaline")

    if "sepsis" in t or "pneumonie" in t or "fièvre" in t:
        actions.append("ATB probabiliste immédiate")

    return f"""
⚡ QUICK ICU — ANALYSE RÉA

🎯 CIBLES : {resp} | {hemo} | {inf}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS :
- {' / '.join(actions) if actions else 'Surveillance + évaluation'}

📝 INPUT : {text}
"""

# =========================================================
# PERFUSION ICU (CORRIGÉ RÉEL RÉA)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]},
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrenaline": "noradrenaline"
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

def calc_real(dose, weight, conc):
    return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2

def perfusion(drug, weight):
    d = DRUGS[drug]

    st.subheader(f"💉 PERFUSION ICU — {drug.upper()} ({weight} kg)")

    factor = st.slider("Ajustement ICU (x)", 0.5, 2.0, st.session_state.dose_factor, 0.1)
    st.session_state.dose_factor = factor

    st.markdown("DOSE | THÉORIQUE | IDE x12 | RÉEL ICU")
    st.markdown("---")

    for dose in d["steps"]:

        theorique = calc_real(dose, weight, d["conc"])
        ide = theorique * 12
        icu = ide * factor

        icu = round(icu * 2) / 2

        st.write(f"{dose} | {theorique} | {round(ide,1)} | {icu}")

# =========================================================
# CHECKLIST DYNAMIQUE (RÉA)
# =========================================================
def checklist(text):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    choc = any(x in t for x in ["choc", "norad", "hypotension"])
    sepsis = any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"])

    base = """
📋 CHECKLIST INTUBATION

☐ matériel OK
☐ capnographie
☐ aspiration
☐ O2 + Ambu
"""

    if hypox:
        base += "\n🫁 HYPOXIE : préoxygénation + PEEP"

    if choc:
        base += "\n🫀 CHOC : noradrénaline prête"

    if sepsis:
        base += "\n🦠 SEPSIS : ATB + cultures"

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
            perfusion(drug, weight)
        else:
            st.markdown("💉 Données manquantes (ex: noradrenaline 70 kg)")

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": str(user_input)})
