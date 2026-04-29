import streamlit as st
import re
from rag_icu import search_icu  # ✅ FIX IMPORT

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.3", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.3")
st.caption("ICU FLOW · Perfusion · Checklist · Quick ICU")

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
# SIDEBAR
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")
    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {"notes": []}
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        selected = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )
        st.session_state.current_patient = selected

elif mode == "PERFUSION ICU":
    st.sidebar.info("Ex : noradrénaline 70kg")

elif mode == "CHECKLIST PLATEAU":
    st.sidebar.info("Ex : intubation")

elif mode == "QUICK ICU":
    st.sidebar.info("Recherche rapide protocole ICU")

# =========================================================
# HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# PERFUSION ICU
# =========================================================
DRUGS = {
    "noradrénaline": {"conc": 0.08, "unit": "µg/kg/min", "doses": [0.05,0.1,0.2,0.5]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "doses": [1,2,3,4]},
    "midazolam": {"conc": 1, "unit": "mg/kg/h", "doses": [0.05,0.1,0.2]},
}

ALIASES = {
    "norad": "noradrénaline",
    "nora": "noradrénaline",
    "propof": "propofol",
    "midaz": "midazolam",
}

def detect(text):
    t = text.lower()
    drug = None
    weight = None

    for a,v in ALIASES.items():
        if a in t:
            drug = v
    for d in DRUGS:
        if d in t:
            drug = d

    w = re.findall(r'(\d{2,3})\s*kg', t)
    if w:
        weight = int(w[0])

    return drug, weight

def calc(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        exact = (dose*weight*60)/(conc*1000)
    else:
        exact = (dose*weight)/conc
    arr = round(exact*2)/2
    return exact, arr

def perf(drug, weight):
    d = DRUGS[drug]
    out = f"💉 **{drug.upper()} — {weight}kg**\n\n"
    out += "| Dose | mL/h IDE | mL/h exact |\n|------|---------|-------------|\n"

    for dose in d["doses"]:
        exact, arr = calc(dose, weight, d["conc"], d["unit"])
        out += f"| {dose} | **{arr}** | ({exact:.2f}) |\n"

    rag = search_icu(drug)
    if rag:
        out += "\n📖 RAG\n"
        for k,v in rag.items():
            out += f"{k.upper()} : {v}\n"

    return out

# =========================================================
# CHECKLIST
# =========================================================
CHECKLIST = {
    "intubation": ["laryngoscope","sonde","ambu","capno","aspiration"]
}

def checklist(text):
    t = text.lower()
    for k in CHECKLIST:
        if k in t:
            out = f"📋 {k.upper()}\n\n"
            for i in CHECKLIST[k]:
                out += f"☐ {i}\n"
            return out
    return "Procédure non reconnue"

# =========================================================
# QUICK ICU
# =========================================================
def quick(query):
    rag = search_icu(query)
    if not rag:
        return "📖 Aucun résultat"

    out = "📚 "
    out += f"CLASSE : {rag.get('classe','-')} \n"
    out += f"💊 USAGE : {rag.get('usage','-')} \n"
    out += f"⚠️ EFFETS : {rag.get('effets','-')} \n"
    out += f"🩺 SURVEILLANCE : {rag.get('surveillance','-')} \n"
    out += f"📌 POINTS ICU : {rag.get('points_icu','-')}"

    return out

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "PERFUSION ICU":
        drug, weight = detect(user_input)

        if not drug:
            answer = "💉 Médicament non reconnu"
        elif not weight:
            answer = "⚠️ poids manquant"
        else:
            answer = perf(drug, weight)

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    elif mode == "QUICK ICU":
        answer = f"⚡ QUICK ICU\n\n{quick(user_input)}"

    elif mode == "ICU FLOW":
        if st.session_state.current_patient:
            st.session_state.patients[st.session_state.current_patient]["notes"].append(user_input)
            answer = "🧠 Donnée ajoutée au patient"
        else:
            answer = "⚠️ créer un patient"

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role":"assistant","content":answer})
