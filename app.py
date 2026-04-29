import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.4", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.4")
st.caption("ICU FLOW · QUICK ICU · PERFUSION · CHECKLIST")

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
# RESET
# =========================================================
if st.sidebar.button("🔄 Reset"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# PATIENT (ICU FLOW ONLY)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter") and new_patient.strip():
        st.session_state.patients[new_patient] = {
            "notes": [],
            "context": []
        }
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHECKLISTS
# =========================================================
CHECKLISTS = {
    "intubation": [
        "laryngoscope",
        "sonde d’intubation",
        "ambu",
        "capnographie",
        "aspiration",
        "monitoring"
    ],
    "voie centrale": [
        "champ stérile",
        "kit VVC",
        "écho",
        "lidocaïne",
        "fil de suture"
    ],
    "arret cardiaque": [
        "défibrillateur",
        "adrénaline",
        "ambu",
        "oxygène",
        "massage cardiaque"
    ]
}

# =========================================================
# RAG SAFE (IMPORTANT FIX)
# =========================================================
def rag(query: str):
    try:
        result = search_icu(query)
        if not result:
            return "Aucun résultat."
        return result
    except:
        return "Erreur RAG"

# =========================================================
# QUICK ICU OUTPUT
# =========================================================
def format_quick(result):
    if isinstance(result, dict):
        return (
            f"📚 CLASSE : {result.get('classe','-')}\n"
            f"💊 USAGE : {result.get('usage','-')}\n"
            f"⚠️ EFFETS : {result.get('effets','-')}\n"
            f"🩺 SURVEILLANCE : {result.get('surveillance','-')}\n"
            f"📌 ICU : {result.get('points_icu','-')}"
        )
    return str(result)

# =========================================================
# PERFUSION ICU SIMPLE
# =========================================================
DRUGS = {
    "noradrenaline": "vasopresseur",
    "midazolam": "benzodiazepine",
    "propofol": "hypnotique",
    "fentanyl": "opioide"
}

def detect_drug(text):
    t = text.lower()
    for d in DRUGS:
        if d in t:
            return d
    return None

# =========================================================
# CHECKLIST DETECTION
# =========================================================
def detect_checklist(text):
    t = text.lower()
    for k in CHECKLISTS:
        if k in t:
            return k
    return None

# =========================================================
# HISTORY
# =========================================================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("ICU input...")

# =========================================================
# MAIN
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # =====================================================
    # ICU FLOW
    # =====================================================
    if mode == "ICU FLOW":

        patient = None
        if st.session_state.current_patient:
            patient = st.session_state.patients[st.session_state.current_patient]

        if patient:
            patient["notes"].append(user_input)

        context = rag(user_input)

        answer = f"""
🧠 ICU FLOW

📖 CONTEXTE
{context}

👉 Patient : {st.session_state.current_patient}
"""

    # =====================================================
    # QUICK ICU (FIXED RAG)
    # =====================================================
    elif mode == "QUICK ICU":

        context = rag(user_input)
        answer = f"""
⚡ QUICK ICU

📖 RAG RESULT
{format_quick(context)}

━━━━━━━━━━━━━━━━━━
👉 ICU ENGINE V10.4
"""

    # =====================================================
    # PERFUSION ICU (RAG SIMPLE)
    # =====================================================
    elif mode == "PERFUSION ICU":

        drug = detect_drug(user_input)

        if not drug:
            answer = "💉 Médicament non reconnu"
        else:
            context = rag(drug)
            answer = f"""
💉 PERFUSION ICU

🔎 DRUG : {drug}

📖 RAG :
{format_quick(context)}

👉 ICU ENGINE V10.4
"""

    # =====================================================
    # CHECKLIST
    # =====================================================
    elif mode == "CHECKLIST PLATEAU":

        proc = detect_checklist(user_input)

        if not proc:
            answer = "📋 Procédure non reconnue"
        else:
            items = "\n".join([f"☐ {i}" for i in CHECKLISTS[proc]])

            answer = f"""
📋 {proc.upper()}

{items}

👉 ICU ENGINE V10.4
"""

    # =====================================================
    # OUTPUT
    # =====================================================
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
