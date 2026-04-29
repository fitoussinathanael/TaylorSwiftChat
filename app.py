import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.2 Lite", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.2 — LITE")
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
# CHECKLISTS
# =========================================================
CHECKLISTS = {
    "intubation": ["laryngoscope", "sonde", "ambu", "capno", "aspiration"],
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
    items = CHECKLISTS[name]
    return "📋 " + name.upper() + "\n\n" + "\n".join(f"☐ {i}" for i in items)

# =========================================================
# ICU FLOW (simplifié mais conservé logique)
# =========================================================
def analyze_flow(text):
    t = text.lower()

    flags = {
        "choc": "choc" in t,
        "vasopresseur": "norad" in t or "vaso" in t,
        "ventilation": "ventil" in t or "intub" in t,
        "sepsis": "sepsis" in t,
        "renal": "creat" in t or "diurese" in t
    }

    if flags["choc"] and flags["vasopresseur"] and flags["sepsis"]:
        return "Choc septique sous vasopresseurs"
    if flags["ventilation"]:
        return "Défaillance respiratoire sous ventilation"
    if flags["renal"]:
        return "Atteinte rénale possible"
    return "État critique à évaluer"

# =========================================================
# PERFUSION ICU (RAG ONLY)
# =========================================================
def perfusion_rag(text):
    context = search_icu(text)
    context = str(context or "").strip()

    return f"""
💉 PERFUSION ICU — RAG MODE

━━━━━━━━━━━━━━━━━━
📖 DONNÉES RAG
{context if context else "Aucune donnée trouvée dans la base."}

━━━━━━━━━━━━━━━━━━
👉 Mode simplifié sans calcul automatique
"""

# =========================================================
# QUICK ICU
# =========================================================
def quick_icu(text):
    context = search_icu(text)
    return f"⚡ QUICK ICU\n\n{context or 'Aucun résultat.'}"

# =========================================================
# ICU FLOW UI
# =========================================================
def icu_flow(text):
    main = analyze_flow(text)
    return f"""
🏥 ICU FLOW

🎯 Situation :
{main}

━━━━━━━━━━━━━━━━━━
👉 ICU ENGINE LITE
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
        answer = perfusion_rag(user_input)

    elif mode == "CHECKLIST PLATEAU":
        proc = detect_procedure(user_input)
        if proc:
            answer = format_checklist(proc)
        else:
            answer = "Procédure non reconnue (intubation / voie centrale / arrêt cardiaque)"

    else:
        answer = "Mode non reconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
