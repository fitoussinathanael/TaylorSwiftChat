import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.6", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.6 STABLE")
st.caption("FLOW · QUICK ICU · PERFUSION MONITOR · CHECKLIST · RAG SAFE")

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
# PATIENTS (FLOW ONLY)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter") and new_patient.strip():
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
def safe_rag(q):
    try:
        res = search_icu(q)
        return res if isinstance(res, dict) else None
    except:
        return None

# =========================================================
# MAP
# =========================================================
def map_calc(text):
    m = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not m:
        return None
    return round((int(m.group(1)) + 2 * int(m.group(2))) / 3, 1)

# =========================================================
# ICU FLOW
# =========================================================
def flow(text):
    t = text.lower()

    resp = 2 if any(x in t for x in ["hypox", "sat", "dysp", "84", "85"]) else 0
    shock = 2 if any(x in t for x in ["choc", "norad", "85/50", "hypotension"]) else 0
    sepsis = 2 if any(x in t for x in ["sepsis", "fièvre", "infection", "pneumonie"]) else 0

    score = resp + shock + sepsis

    severity = "🔴 CRITIQUE" if score >= 4 else "🟠 SÉVÈRE" if score >= 2 else "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW

🫁 RESP : {resp} | 🫀 CHOC : {shock} | 🦠 SEPSIS : {sepsis}
⚠️ GRAVITÉ : {severity}

🩺 PAM : {map_calc(text) or "N/A"}
"""

# =========================================================
# QUICK ICU (FIX IMPORTANT)
# - plus jamais "aucun résultat brut"
# - fallback clinique intelligent
# =========================================================
def quick(text):
    rag = safe_rag(text)

    if rag:
        return f"""
⚡ QUICK ICU

📦 Classe : {rag.get('classe','-')}
💊 Usage : {rag.get('usage','-')}
⚠️ Effets : {rag.get('effets','-')}
🩺 Surveillance : {rag.get('surveillance','-')}
"""

    # FALLBACK ICU CLINIQUE (IMPORTANT)
    t = text.lower()

    resp = "hypox" in t or "sat" in t
    shock = "choc" in t or "norad" in t
    sepsis = "fièvre" in t or "infection" in t or "pneumonie" in t

    actions = []

    if resp:
        actions.append("🫁 Oxygène / VNI / intubation si échec")
    if shock:
        actions.append("🫀 Remplissage + noradrénaline")
    if sepsis:
        actions.append("🦠 ATB probabiliste immédiate")

    severity = "🔴 CRITIQUE" if (resp and shock) else "🟠 SÉVÈRE" if (resp or shock or sepsis) else "🟡 MODÉRÉ"

    return f"""
⚡ QUICK ICU — ANALYSE RÉA

🎯 CIBLES :
{" | ".join([
"🫁 SpO2 > 92%",
"🫀 PAM ≥ 65 mmHg",
"🦠 ATB < 1h"
])}

⚠️ GRAVITÉ : {severity}

🧠 ACTIONS :
{chr(10).join(actions) if actions else "Surveillance clinique"}

📝 INPUT : {text}
"""

# =========================================================
# PERFUSION ICU (STABLE + TABLEAU LISIBLE)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "steps": [1, 2, 3, 4]}
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrenaline": "noradrenaline",
    "propofol": "propofol"
}

def detect(text):
    t = text.lower()
    drug = next((v for k,v in ALIASES.items() if k in t), None)

    w = re.findall(r'(\d{2,3})\s*kg', t)
    weight = int(w[0]) if w else None

    return drug, weight

def calc(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2
    return round(((dose * weight) / conc) * 2) / 2

def perfusion(drug, weight):
    d = DRUGS[drug]

    st.subheader(f"💉 PERFUSION — {drug.upper()} ({weight} kg)")

    factor = st.slider("Titration ICU", 0.5, 2.0, st.session_state.dose_factor, 0.1)
    st.session_state.dose_factor = factor

    st.markdown("DOSE | IDEAL | RÉEL")

    for dose in d["steps"]:
        base = calc(dose, weight, d["conc"], d["unit"])
        real = round(base * factor * 2) / 2
        st.write(f"{dose} | {base} | {real}")

# =========================================================
# CHECKLIST DYNAMIQUE
# =========================================================
def checklist(text):
    t = text.lower()

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    shock = any(x in t for x in ["choc", "norad"])
    sepsis = any(x in t for x in ["sepsis", "infection"])

    base = "📋 CHECKLIST INTUBATION\n☐ matériel\n☐ capno\n☐ aspiration\n"

    if hypox:
        base += "\n🫁 HYPOXIE : préoxygénation + PEEP"
    if shock:
        base += "\n🫀 CHOC : noradrénaline prête"
    if sepsis:
        base += "\n🦠 SEPSIS : ATB rapide"

    return base

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = flow(user_input)
        st.markdown(answer)

    elif mode == "QUICK ICU":
        answer = quick(user_input)
        st.markdown(answer)

    elif mode == "PERFUSION ICU":
        drug, weight = detect(user_input)

        if drug and weight:
            perfusion(drug, weight)
        else:
            st.markdown("💉 Données manquantes (ex: noradrenaline 70 kg)")

    elif mode == "CHECKLIST PLATEAU":
        st.markdown(checklist(user_input))

    st.session_state.messages.append({"role": "assistant", "content": str(user_input)})
