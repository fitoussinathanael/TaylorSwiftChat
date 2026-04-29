import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.2", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.2")
st.caption("ICU FLOW · Perfusion · Checklist · IA Clinique")

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
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU", "IA CLINIQUE"]
)

# =========================================================
# SIDEBAR CONTEXTUELLE
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")
    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {
            "cibles": {
                "hemodynamique": [], "respiratoire": [],
                "neuro": [], "renal": [], "infectieux": []
            },
            "numerics": {
                "pam": [], "norad": [], "fio2": [], "pf_ratio": [],
                "diurese": [], "creatinine": [], "lactate": [],
                "temperature": [], "spo2": []
            },
            "notes": []
        }
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    patient_list = list(st.session_state.patients.keys())
    if patient_list:
        selected = st.sidebar.selectbox(
            "Patient actif", patient_list,
            index=patient_list.index(st.session_state.current_patient)
            if st.session_state.current_patient in patient_list else 0
        )
        st.session_state.current_patient = selected

elif mode == "PERFUSION ICU":
    st.sidebar.info("Ex: noradrénaline 70kg")

elif mode == "CHECKLIST PLATEAU":
    st.sidebar.info("Ex: intubation, voie centrale")

elif mode == "IA CLINIQUE":
    st.sidebar.info("Ex: sepsis-3, SDRA")

elif mode == "QUICK ICU":
    st.sidebar.info("Transmission rapide RAG")

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
# PERFUSION ICU CORE SAFE
# =========================================================

CONCENTRATIONS = {
    "noradrénaline": {"concentration_mg_ml": 0.08, "unité": "µg/kg/min", "paliers": [0.05,0.1,0.15,0.2,0.3,0.5,0.8,1.0], "fiche_rag": "noradrénaline"},
    "adrénaline": {"concentration_mg_ml": 0.04, "unité": "µg/kg/min", "paliers": [0.05,0.1,0.2,0.3,0.5], "fiche_rag": "adrénaline"},
    "dobutamine": {"concentration_mg_ml": 1.0, "unité": "µg/kg/min", "paliers": [2.5,5,7.5,10,15,20], "fiche_rag": "dobutamine"},
    "propofol": {"concentration_mg_ml": 10.0, "unité": "mg/kg/h", "paliers": [1,2,3,4,5,6], "fiche_rag": "propofol"},
}

ALIASES = {
    "norad": "noradrénaline",
    "nora": "noradrénaline",
    "adré": "adrénaline",
    "dobu": "dobutamine",
    "propofol": "propofol",
}

def detect_drug_and_weight(text):
    t = text.lower()
    drug = None
    weight = None

    for a, c in ALIASES.items():
        if a in t:
            drug = c
            break

    w = re.findall(r'(\d{2,3})\s*(?:kg)?', t)
    if w:
        weight = int(w[-1])

    return drug, weight


def calc_debit(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        val = (dose * weight * 60) / (conc * 1000)
    elif unit == "mg/kg/h":
        val = (dose * weight) / conc
    else:
        val = dose

    return val, round(val * 2) / 2


def format_perf(drug, weight, data, rag):
    lines = []
    lines.append(f"💉 {drug} — {weight}kg")
    lines.append(f"Concentration {data['concentration_mg_ml']} mg/mL")

    for d in data["paliers"]:
        v, r = calc_debit(d, weight, data["concentration_mg_ml"], data["unité"])
        lines.append(f"{d} → {r} mL/h ({v:.2f})")

    rag_text = str(rag or "").strip()
    if rag_text:
        lines.append("\nRAG:")
        lines.append(rag_text)

    return "\n".join(lines)

# =========================================================
# QUICK ICU SAFE
# =========================================================

def quick_icu(query):
    res = search_icu(query)
    txt = str(res or "")
    return txt if txt else "Aucun résultat dans la base."

# =========================================================
# CHECKLIST SIMPLE
# =========================================================

CHECKLISTS = {
    "intubation": ["laryngoscope", "sonde", "ambu", "capno"],
    "voie centrale": ["kit VVC", "écho", "champ stérile"],
}

def detect_proc(t):
    t = t.lower()
    for k in CHECKLISTS:
        if k in t:
            return k
    return None

# =========================================================
# IA CLINIQUE SAFE SIMPLE
# =========================================================

def ia_clinique(q):
    r = search_icu(q)
    r = str(r or "")

    if "sepsis" in q.lower():
        return "Sepsis-3 : infection + SOFA ≥2 + lactate >2"
    if "sdra" in q.lower():
        return "SDRA : P/F <300 + infiltrats bilatéraux"
    return r or "Analyse IA non spécifique"

# =========================================================
# ICU FLOW SAFE (VERSION STABLE SIMPLIFIÉE)
# =========================================================

def safe(x):
    return x[0] if x else None

# =========================================================
# DISPATCH
# =========================================================

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    if mode == "PERFUSION ICU":
        drug, weight = detect_drug_and_weight(user_input)

        if not drug:
            answer = "Médicament non reconnu"
        elif not weight:
            answer = "Poids manquant"
        else:
            data = CONCENTRATIONS[drug]
            rag = search_icu(data["fiche_rag"])
            answer = format_perf(drug, weight, data, rag)

    elif mode == "QUICK ICU":
        answer = "⚡ QUICK ICU\n\n" + quick_icu(user_input)

    elif mode == "CHECKLIST PLATEAU":
        p = detect_proc(user_input)
        answer = "\n".join(CHECKLISTS.get(p, ["Procédure inconnue"]))

    elif mode == "IA CLINIQUE":
        answer = ia_clinique(user_input)

    elif mode == "ICU FLOW":
        answer = "ICU FLOW simplifié stable (version patch safe)"

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
