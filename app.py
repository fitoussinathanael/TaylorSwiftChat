import streamlit as st
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V8", page_icon="🏥", layout="wide")

# =========================================================
# HEADER
# =========================================================
st.title("🏥 ICU ENGINE")
st.caption("ICU FLOW decision support - stable mode")

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
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU REAL", "PERFUSION TERRAIN", "IA CLINIQUE"]
)

# =========================================================
# PATIENT MANAGEMENT
# =========================================================
st.sidebar.markdown("## 🧠 ICU FLOW")

new_patient = st.sidebar.text_input("Créer patient")

if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():

    st.session_state.patients[new_patient] = {
        "cibles": {
            "hemodynamique": [],
            "respiratoire": [],
            "neuro": [],
            "renal": [],
            "infectieux": []
        },
        "notes": []
    }

    st.session_state.current_patient = new_patient
    st.success(f"Patient créé : {new_patient}")

patient_list = list(st.session_state.patients.keys())

if patient_list:
    selected = st.sidebar.selectbox(
        "Patient actif",
        patient_list,
        index=patient_list.index(st.session_state.current_patient)
        if st.session_state.current_patient in patient_list else 0
    )
    st.session_state.current_patient = selected

# =========================================================
# RESET
# =========================================================
if st.sidebar.button("Reset session"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Entrée ICU...")

# =========================================================
# 🧠 CLINICAL ENGINE (NO FAN OUT)
# =========================================================
def extract_clinical(text):
    t = text.lower()

    data = {
        "hemodynamique": [],
        "respiratoire": [],
        "neuro": [],
        "renal": [],
        "infectieux": []
    }

    if "norad" in t or "nora" in t:
        data["hemodynamique"].append("noradrénaline en cours")
    if "hypotension" in t or "map" in t:
        data["hemodynamique"].append("instabilité tensionnelle")

    if "ventil" in t or "intub" in t or "peep" in t:
        data["respiratoire"].append("ventilation mécanique")

    if "propof" in t:
        data["neuro"].append("propofol")
    if "midaz" in t:
        data["neuro"].append("midazolam")
    if "agitation" in t:
        data["neuro"].append("agitation initiale")

    if "creat" in t or "diurese" in t:
        data["renal"].append("fonction rénale à surveiller")

    if "sepsis" in t or "infection" in t:
        data["infectieux"].append("sepsis suspect")
    if "fièvre" in t or "38" in t:
        data["infectieux"].append("syndrome fébrile")

    return data

def clinical_summary(text):
    t = text.lower()
    summary = []

    if "norad" in t:
        summary.append("support vasopresseur actif")
    if "hypotension" in t or "map" in t:
        summary.append("instabilité hémodynamique")

    if "ventil" in t:
        summary.append("ventilation mécanique invasive")
    if "propof" in t or "midaz" in t:
        summary.append("sédation IV continue")

    if "sepsis" in t:
        summary.append("tableau infectieux sévère suspect")

    return summary

# =========================================================
# FLOW MODE
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        patient = st.session_state.patients[st.session_state.current_patient]

        extracted = extract_clinical(user_input)

        # MEMORY UPDATE
        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]:
                    patient["cibles"][k].append(item)

        if not any(extracted.values()):
            patient["notes"].append(user_input)

        def clean(lst):
            return " / ".join(lst[-3:]) if lst else "aucune"

        st.session_state.messages.append({"role": "user", "content": user_input})

        answer = f"""
🏥 ICU ENGINE - FLOW MODE

━━━━━━━━━━━━━━━━━━

🫀 HÉMODYNAMIQUE
{clean(patient["cibles"]["hemodynamique"])}

🫁 RESPIRATOIRE
{clean(patient["cibles"]["respiratoire"])}

🧠 NEURO
{clean(patient["cibles"]["neuro"])}

🧪 RÉNAL
{clean(patient["cibles"]["renal"])}

🦠 INFECTIEUX
{clean(patient["cibles"]["infectieux"])}

━━━━━━━━━━━━━━━━━━

🧠 SYNTHÈSE CLINIQUE
- {" / ".join(clinical_summary(user_input)) if clinical_summary(user_input) else "stable"}

📝 NOTES
{clean(patient["notes"])}

👉 ICU ENGINE ACTIVE
"""

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# =========================================================
# CLASSIC MODES
# =========================================================
else:

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        context = search_icu(user_input)

        if mode == "QUICK ICU":
            answer = f"⚡ QUICK ICU\n\n{context or 'non documenté'}"

        elif mode == "PERFUSION ICU REAL":
            answer = "💉 PERFUSION ICU REAL"

        elif mode == "PERFUSION TERRAIN":
            answer = "🏥 PERFUSION TERRAIN"

        else:
            answer = f"🧠 IA ICU\n\n{user_input}\n\n{context}"

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
