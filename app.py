import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V9", page_icon="🏥")

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patients" not in st.session_state:
    st.session_state.patients = {}

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine V9 - FLOW + MEMORY")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION ICU REAL", "PERFUSION TERRAIN", "IA CLINIQUE", "ICU FLOW"]
)

# -----------------------------
# PATIENT MANAGEMENT (FLOW MODE)
# -----------------------------
st.sidebar.markdown("## 🧠 ICU FLOW")

new_patient = st.sidebar.text_input("Créer patient")

if st.sidebar.button("➕ Ajouter patient") and new_patient:
    st.session_state.patients[new_patient] = {
        "cibles": {
            "hemodynamique": "",
            "respiratoire": "",
            "neuro": "",
            "renal": "",
            "infectieux": ""
        },
        "notes": [],
        "alerts": []
    }
    st.session_state.current_patient = new_patient

patient_list = list(st.session_state.patients.keys())

if patient_list:
    st.session_state.current_patient = st.sidebar.selectbox(
        "Patient actif",
        patient_list
    )

if st.sidebar.button("Reset messages"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Entrée ICU...")

# =========================================================
# FLOW MODE (NEW)
# =========================================================
if mode == "ICU FLOW":

    if user_input and st.session_state.current_patient:

        p = st.session_state.patients[st.session_state.current_patient]

        text = user_input.lower()

        # auto routing simple
        if "tension" in text or "norad" in text:
            p["cibles"]["hemodynamique"] = user_input

        elif "ventilation" in text or "intub" in text:
            p["cibles"]["respiratoire"] = user_input

        elif "glasgow" in text or "sedation" in text:
            p["cibles"]["neuro"] = user_input

        elif "creat" in text or "diurese" in text:
            p["cibles"]["renal"] = user_input

        elif "infection" in text or "sepsis" in text:
            p["cibles"]["infectieux"] = user_input

        else:
            p["notes"].append(user_input)

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):

            answer = f"""
🏥 ICU FLOW - {st.session_state.current_patient}

🫀 HÉMODYNAMIQUE : {p['cibles']['hemodynamique']}
🫁 RESPIRATOIRE : {p['cibles']['respiratoire']}
🧠 NEURO : {p['cibles']['neuro']}
🧪 RÉNAL : {p['cibles']['renal']}
🦠 INFECTIEUX : {p['cibles']['infectieux']}

📝 NOTES :
- {' / '.join(p['notes'][-3:]) if p['notes'] else 'aucune'}

⚠ ALERTES :
- {'aucune'}

👉 Mode mémoire active ICU FLOW
"""

            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

# =========================================================
# CLASSIC MODES
# =========================================================
else:

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        context = search_icu(user_input)

        # -----------------------------
        # QUICK ICU
        # -----------------------------
        if mode == "QUICK ICU":

            if context and context != "non documenté dans la base ICU":
                answer = f"""
⚡ QUICK ICU

💊 Médicament : {user_input}

📦 Données :
{context}

👉 Action : surveillance clinique
"""
            else:
                answer = "⚡ QUICK ICU\n→ non documenté"

        # -----------------------------
        # PERFUSION REAL
        # -----------------------------
        elif mode == "PERFUSION ICU REAL":

            text = user_input.lower()
            weight = 70

            for w in text.split():
                if w.isdigit():
                    weight = int(w)

            drugs = {
                "norad": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160},
                "nora": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160},
                "propof": {"dose": 2, "unit": "mg/kg/h", "conc": 10},
                "fenta": {"dose": 2, "unit": "µg/kg/h", "conc": 50},
                "midaz": {"dose": 0.05, "unit": "mg/kg/h", "conc": 1}
            }

            found = None
            for k in drugs:
                if k in text:
                    found = k

            if found:
                d = drugs[found]

                if "µg" in d["unit"]:
                    ml_h = (d["dose"] * weight * 60) / d["conc"]
                else:
                    ml_h = (d["dose"] * weight) / d["conc"]

                answer = f"""
💉 PERFUSION ICU REAL

👉 {round(ml_h,2)} mL/h
"""
            else:
                answer = "médicament non reconnu"

        # -----------------------------
        # PERFUSION TERRAIN
        # -----------------------------
        elif mode == "PERFUSION TERRAIN":

            text = user_input.lower()
            weight = 70

            for w in text.split():
                if w.isdigit():
                    weight = int(w)

            drugs = {
                "norad": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160},
                "nora": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160}
            }

            found = None
            for k in drugs:
                if k in text:
                    found = k

            if found:
                d = drugs[found]

                ml_h = (d["dose"] * weight * 60) / d["conc"]
                ml_round = round(ml_h * 2) / 2

                answer = f"""
🏥 PERFUSION TERRAIN

👉 {ml_round} mL/h
(≈ {round(ml_h,2)})
"""
            else:
                answer = "non reconnu"

        # -----------------------------
        # IA CLINIQUE
        # -----------------------------
        else:

            answer = f"""
🧠 IA ICU

{user_input}

{context}
"""

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
