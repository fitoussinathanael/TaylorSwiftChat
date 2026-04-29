import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.3", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.3 — STABLE")
st.caption("ICU FLOW · QUICK ICU · PERFUSION RAG · CHECKLIST")

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
# PATIENT MANAGEMENT (RESTORED)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {"notes": []}
        st.session_state.current_patient = new_patient
        st.success(f"Patient ajouté : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHECKLISTS
# =========================================================
CHECKLISTS = {
    "intubation": ["laryngoscope", "sonde IOT", "ambu", "capnographe", "aspiration"],
    "voie centrale": ["kit VVC", "champ stérile", "échographe", "fil", "pansement"],
    "arrêt cardiaque": ["chariot", "défibrillateur", "adrénaline", "ambu", "monitoring"]
}

def detect_procedure(text):
    t = text.lower()
    for k in CHECKLISTS:
        if k in t:
            return k
    return None

def format_checklist(name):
    return (
        f"📋 {name.upper()}\n\n" +
        "\n".join(f"☐ {i}" for i in CHECKLISTS[name])
    )

# =========================================================
# SAFE RAG WRAPPER (IMPORTANT FIX)
# =========================================================
def safe_rag(query):
    try:
        result = search_icu(query)
        return str(result or "").strip()
    except Exception as e:
        return f"⚠️ RAG ERROR: {e}"

# =========================================================
# ICU FLOW (SIMPLE BUT FUNCTIONAL)
# =========================================================
def icu_flow(text):
    t = text.lower()

    flags = {
        "choc": "choc" in t,
        "vasopresseur": "norad" in t or "vaso" in t,
        "ventilation": "ventil" in t or "intub" in t,
        "sepsis": "sepsis" in t,
        "renal": "creat" in t or "diurese" in t
    }

    if flags["choc"] and flags["vasopresseur"] and flags["sepsis"]:
        main = "Choc septique sous vasopresseurs"
    elif flags["ventilation"]:
        main = "Défaillance respiratoire sous ventilation"
    elif flags["renal"]:
        main = "Atteinte rénale suspectée"
    else:
        main = "État critique à évaluer"

    return f"""
🏥 ICU FLOW

🎯 PROBLÈME PRINCIPAL
{main}

━━━━━━━━━━━━━━━━━━
👉 ICU ENGINE V10.3
"""

# =========================================================
# QUICK ICU
# =========================================================
def quick_icu(text):
    context = safe_rag(text)

    return f"""
⚡ QUICK ICU

📖 RAG RESULT
{context if context else "Aucun résultat."}

━━━━━━━━━━━━━━━━━━
👉 ICU ENGINE V10.3
"""

# =========================================================
# PERFUSION ICU (RAG ONLY)
# =========================================================
def perfusion_icu(text):
    context = safe_rag(text)

    return f"""
💉 PERFUSION ICU (RAG MODE)

━━━━━━━━━━━━━━━━━━
📖 CONTEXTE RAG
{context if context else "Aucune donnée disponible"}

━━━━━━━━━━━━━━━━━━
⚠️ Mode sans calcul automatique
👉 ICU ENGINE V10.3
"""

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
        proc = detect_procedure(user_input)
        answer = format_checklist(proc) if proc else "Procédure non reconnue"

    else:
        answer = "Mode non reconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
