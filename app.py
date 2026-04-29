import streamlit as st
import re

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU ENGINE CORE", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE CORE")

# =========================================================
# SESSION STATE (STABLE)
# =========================================================
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
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST"]
)

# =========================================================
# PATIENT SYSTEM (FIX STABLE MEMORY)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 PATIENTS")

    new_patient = st.sidebar.text_input("Nom patient")

    if st.sidebar.button("➕ Ajouter patient"):
        if new_patient.strip():
            st.session_state.patients[new_patient] = {
                "notes": [],
                "last_input": ""
            }
            st.session_state.current_patient = new_patient
            st.success(f"Patient ajouté : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Entrée ICU...")

# =========================================================
# QUICK ICU ENGINE (STABLE CLINICAL LOGIC)
# =========================================================
def quick_icu(text):
    t = text.lower()

    resp = any(x in t for x in ["dysp", "hypox", "sat", "86%", "o2"])
    choc = any(x in t for x in ["ta", "hypotension", "choc", "norad"])
    sepsis = any(x in t for x in ["fièvre", "infection", "pneumonie", "sepsis"])

    severity = "🟡 MODÉRÉ"
    if resp and choc:
        severity = "🟠 SÉVÈRE"
    if resp and choc and sepsis:
        severity = "🔴 CRITIQUE"

    targets = []
    actions = []

    if resp:
        targets.append("🫁 SpO2 > 92%")
        actions.append("Oxygène / VNI / intubation si échec")

    if choc:
        targets.append("🫀 PAM ≥ 65 mmHg")
        actions.append("Remplissage + noradrénaline")

    if sepsis:
        targets.append("🦠 ATB < 1h + contrôle source")
        actions.append("ATB probabiliste immédiate")

    return f"""
🧠 QUICK ICU — ANALYSE RÉA

🎯 CIBLES : {" | ".join(targets) if targets else "Surveillance"}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS :
- {'\n- '.join(actions) if actions else 'Surveillance clinique'}

📝 INPUT :
{text}
"""

# =========================================================
# PERFUSION ICU (×12 TERRAIN + TABLE PROPRE)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]}
}

def detect_drug(text):
    t = text.lower()
    if "norad" in t:
        return "noradrenaline"
    return None

def detect_weight(text):
    m = re.findall(r'(\d{2,3})\s*kg', text.lower())
    return int(m[0]) if m else None

def calc(dose, weight, conc):
    return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2

def perfusion(drug, weight):
    d = DRUGS[drug]
    factor = st.session_state.dose_factor

    st.subheader(f"💉 PERFUSION ICU — {drug.upper()} ({weight} kg)")

    st.session_state.dose_factor = st.slider("Facteur terrain (× ICU)", 0.5, 2.0, factor, 0.1)

    st.markdown("DOSE | IDEAL | TERRAIN ×12 | RÉEL")

    for dose in d["steps"]:
        base = calc(dose, weight, d["conc"])
        terrain = round(base * 1.2, 2)
        real = round(base * st.session_state.dose_factor, 2)

        st.write(f"{dose} | {base} | {terrain} | {real}")

# =========================================================
# CHECKLIST DYNAMIQUE
# =========================================================
def checklist(text):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    choc = any(x in t for x in ["choc", "ta", "norad"])
    sepsis = any(x in t for x in ["sepsis", "fièvre", "pneumonie"])

    base = """
📋 CHECKLIST INTUBATION

☐ matériel
☐ aspiration
☐ capnographie
☐ médicaments
☐ plan B
☐ équipe prête
"""

    if hypox:
        base += "\n🫁 HYPOXIE → préoxygénation + PEEP"

    if choc:
        base += "\n🫀 CHOC → noradrénaline prête"

    if sepsis:
        base += "\n🦠 SEPSIS → ATB immédiate"

    return base

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    if mode == "ICU FLOW":
        st.write("🧠 ICU FLOW actif")
        st.write(user_input)

    elif mode == "QUICK ICU":
        st.markdown(quick_icu(user_input))

    elif mode == "PERFUSION ICU":
        drug = detect_drug(user_input)
        weight = detect_weight(user_input)
        if drug and weight:
            perfusion(drug, weight)
        else:
            st.warning("💉 noradrenaline + poids requis (ex: 70 kg)")

    elif mode == "CHECKLIST":
        st.markdown(checklist(user_input))
