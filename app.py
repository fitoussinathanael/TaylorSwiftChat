import streamlit as st
import re
import unicodedata
from rag__ICU import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.5", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.5")

# =========================================================
# SESSION
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

if st.sidebar.button("🔄 Reset"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# PATIENT (ICU FLOW)
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
# HISTORY
# =========================================================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("ICU input...")

# =========================================================
# NORMALISATION ACCENTS
# =========================================================
def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII").lower()

# =========================================================
# RAG SAFE
# =========================================================
def safe_rag(query):
    try:
        return search_icu(query)
    except:
        return None

def format_rag(data):
    if not data:
        return "📖 RAG RESULT Aucun résultat."
    return (
        f"📚 CLASSE : {data.get('classe','-')}\n"
        f"💊 USAGE : {data.get('usage','-')}\n"
        f"⚠️ EFFETS : {data.get('effets','-')}\n"
        f"🩺 SURVEILLANCE : {data.get('surveillance','-')}\n"
        f"📌 ICU : {data.get('points_icu','-')}"
    )

# =========================================================
# PERFUSION ICU (AVEC DOUBLE CALCUL)
# =========================================================
def detect_drug(text):
    t = normalize(text)

    drugs = {
        "noradrenaline": "noradrenaline",
        "midazolam": "midazolam",
        "propofol": "propofol",
        "fentanyl": "fentanyl",
        "dobutamine": "dobutamine",
        "potassium": "potassium",
        "kcl": "potassium"
    }

    for k, v in drugs.items():
        if k in t:
            return v

    return None

def detect_weight(text):
    m = re.findall(r'(\d{2,3})\s*kg', text.lower())
    return int(m[-1]) if m else None

# 🔥 CALCUL PERFUSION ICU
def perfusion_calc(drug, weight):

    # dose fictive simple ICU (démo terrain)
    base_dose = {
        "noradrenaline": 0.1,  # µg/kg/min
        "dobutamine": 5,
        "propofol": 2,
        "midazolam": 0.05,
        "fentanyl": 2
    }

    dose = base_dose.get(drug, 1)

    # ⚠️ CALCUL PRÉCIS
    precise = dose * weight

    # 🔥 MÉTHODE INFIRMIÈRE (×12 simplifié)
    nurse = round((precise * 12) / 12, 0)

    return precise, nurse

def perfusion_output(drug, weight):

    rag = safe_rag(drug)
    precise, nurse = perfusion_calc(drug, weight)

    return f"""
💉 PERFUSION ICU

🧪 Médicament : {drug}
⚖️ Poids : {weight} kg

━━━━━━━━━━━━━━
📊 CALCUL

🔬 Valeur précise :
({precise:.2f} mL/h ou équivalent)

🩺 Méthode infirmière (×12) :
{nurse:.0f} mL/h

━━━━━━━━━━━━━━
{format_rag(rag)}

👉 ICU ENGINE V10.5
"""

# =========================================================
# CHECKLIST
# =========================================================
CHECKS = {
    "intubation": ["laryngoscope","sonde","ambu","capno","aspiration"],
    "voie centrale": ["champ stérile","kit VVC","lidocaïne","monitoring"],
    "arret cardiaque": ["défibrillateur","adrénaline","ambu","ECG"]
}

def detect_check(text):
    t = normalize(text)
    for k in CHECKS:
        if k in t:
            return k
    return None

def format_check(name):
    return "📋 " + name.upper() + "\n\n" + "\n".join([f"☐ {i}" for i in CHECKS[name]])

# =========================================================
# QUICK ICU
# =========================================================
def quick_icu(text):
    rag = safe_rag(text)
    return f"""
⚡ QUICK ICU

📖 RAG RESULT
{format_rag(rag)}

👉 ICU ENGINE V10.5
"""

# =========================================================
# ICU FLOW
# =========================================================
def icu_flow(text):
    return f"""
🧠 ICU FLOW

Patient : {st.session_state.current_patient or "NON SÉLECTIONNÉ"}

Entrée : {text}

👉 MODE STABLE V10.5
"""

# =========================================================
# MAIN
# =========================================================
if user_input:

    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # QUICK ICU
    if mode == "QUICK ICU":
        answer = quick_icu(user_input)

    # PERFUSION ICU
    elif mode == "PERFUSION ICU":

        drug = detect_drug(user_input)
        weight = detect_weight(user_input)

        if not drug:
            answer = "💉 Médicament non reconnu"
        elif not weight:
            answer = "⚠️ Poids manquant (ex: 70kg)"
        else:
            answer = perfusion_output(drug, weight)

    # CHECKLIST
    elif mode == "CHECKLIST PLATEAU":

        proc = detect_check(user_input)
        answer = format_check(proc) if proc else "Procédure non reconnue"

    # ICU FLOW
    else:
        answer = icu_flow(user_input)

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role":"assistant","content":answer})
