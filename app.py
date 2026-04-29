import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.3", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.3")
st.caption("ICU FLOW · QUICK ICU · PERFUSION · CHECKLIST · IA")

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
# SIDEBAR PATIENT (ICU FLOW)
# =========================================================
if mode == "ICU FLOW":

    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {
            "notes": [],
            "numerics": {"pam": [], "norad": [], "fio2": [], "lactate": []}
        }
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHECK RESET
# =========================================================
if st.sidebar.button("🔄 Reset session"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# ICU FLOW (ULTRA SIMPLIFIÉ MAIS STABLE)
# =========================================================
def icu_flow(text):
    t = text.lower()

    flags = {
        "sepsis": "sepsis" in t,
        "choc": "choc" in t,
        "vasopresseur": "norad" in t or "noradr" in t,
        "ventilation": "ventil" in t or "intub" in t,
        "renal": "créat" in t or "diurese" in t
    }

    if flags["sepsis"] and flags["choc"] and flags["vasopresseur"]:
        return "🟥 CHOC SEPTIQUE VASOPLÉGIQUE → noradrénaline + ATB immédiate"

    if flags["sepsis"]:
        return "🟧 SEPSIS SUSPECTÉ → lactate + hémocultures + antibiothérapie"

    if flags["ventilation"]:
        return "🫁 DETRESSE RESPIRATOIRE → optimisation ventilation / gaz du sang"

    if flags["renal"]:
        return "🧪 ALTÉRATION RÉNALE → surveillance diurèse / créatinine"

    return "🟡 ÉVALUATION ICU GLOBALE REQUISE"

# =========================================================
# QUICK ICU (CORRIGÉ + FORMATÉ)
# =========================================================
def quick_icu(text):
    context = search_icu(text)

    if not context:
        return (
            "⚡ QUICK ICU\n\n"
            "📖 RAG RESULT Aucun résultat.\n\n"
            "👉 ICU ENGINE V10.3"
        )

    return f"""
⚡ QUICK ICU

📚 CLASSE : {context.get('classe','-')}
💊 USAGE : {context.get('usage','-')}
⚠️ EFFETS : {context.get('effets','-')}
🩺 SURVEILLANCE : {context.get('surveillance','-')}
📌 POINTS ICU : {context.get('points_icu','-')}

👉 ICU ENGINE V10.3
"""

# =========================================================
# PERFUSION ICU (SIMPLE RAG ONLY)
# =========================================================
def perfusion_icu(text):
    context = search_icu(text)

    if not context:
        return "💉 PERFUSION ICU\n\nMédicament non reconnu dans RAG."

    return f"""
💉 PERFUSION ICU

📚 {context.get('classe','')}
💊 {context.get('usage','')}
⚠️ {context.get('effets','')}
🩺 {context.get('surveillance','')}

👉 ICU ENGINE V10.3
"""

# =========================================================
# CHECKLIST (SIMPLE MAIS STABLE)
# =========================================================
CHECKLISTS = {
    "intubation": ["laryngoscope", "sonde", "ambu", "capno", "aspiration"],
    "voie centrale": ["kit VVC", "champ stérile", "écho", "lidocaïne"],
    "ACR": ["défibrillateur", "adrénaline", "ambu", "monitoring"]
}

def checklist(text):
    t = text.lower()
    for k, v in CHECKLISTS.items():
        if k in t:
            return "📋 " + k.upper() + "\n\n" + "\n".join("☐ " + i for i in v)
    return "📋 Procédure non reconnue"

# =========================================================
# MAIN DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = icu_flow(user_input)

    elif mode == "QUICK ICU":
        answer = quick_icu(user_input)

    elif mode == "PERFUSION ICU":
        answer = perfusion_icu(user_input)

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
