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
st.title("🏥 ICU Engine V9 - FLOW V4 + MEMORY")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION ICU REAL", "PERFUSION TERRAIN", "IA CLINIQUE", "ICU FLOW"]
)

# -----------------------------
# PATIENT MANAGEMENT
# -----------------------------
st.sidebar.markdown("## 🧠 ICU FLOW")

new_patient = st.sidebar.text_input("Créer patient")

if st.sidebar.button("➕ Ajouter patient") and new_patient:

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

# -----------------------------
# RESET
# -----------------------------
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
# ICU FLOW V4 (INTELLIGENT + SCORED)
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        p = st.session_state.patients[st.session_state.current_patient]
        text = user_input.lower()

        # -----------------------------
        # SCORES CLINIQUES
        # -----------------------------
        scores = {
            "hemodynamique": 0,
            "respiratoire": 0,
            "neuro": 0,
            "renal": 0,
            "infectieux": 0
        }

        risks = []

        # -----------------------------
        # DETECTION CLINIQUE
        # -----------------------------
        if "norad" in text or "nora" in text:
            scores["hemodynamique"] += 3
            risks.append("instabilité hémodynamique")

        if "tension" in text:
            scores["hemodynamique"] += 2

        if "propof" in text:
            scores["neuro"] += 3
            risks.append("risque hypotension / sédation")

        if "midaz" in text:
            scores["neuro"] += 2

        if "fenta" in text:
            scores["respiratoire"] += 2
            risks.append("dépression respiratoire")

        if "intub" in text or "ventil" in text:
            scores["respiratoire"] += 3

        if "creat" in text or "diurese" in text:
            scores["renal"] += 2

        if "sepsis" in text or "infection" in text:
            scores["infectieux"] += 4
            risks.append("risque choc septique")

        if "hypotension" in text:
            scores["hemodynamique"] += 2

        # -----------------------------
        # ROUTING + MEMORY
        # -----------------------------
        if scores["hemodynamique"] > 0:
            p["cibles"]["hemodynamique"].append(user_input)

        if scores["respiratoire"] > 0:
            p["cibles"]["respiratoire"].append(user_input)

        if scores["neuro"] > 0:
            p["cibles"]["neuro"].append(user_input)

        if scores["renal"] > 0:
            p["cibles"]["renal"].append(user_input)

        if scores["infectieux"] > 0:
            p["cibles"]["infectieux"].append(user_input)

        if sum(scores.values()) == 0:
            p["notes"].append(user_input)

        # -----------------------------
        # TOP CIBLES
        # -----------------------------
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        main_target = sorted_scores[0][0]
        secondary_targets = [x[0] for x in sorted_scores[1:] if x[1] > 0]

        # -----------------------------
        # STORE MESSAGE
        # -----------------------------
        st.session_state.messages.append({"role": "user", "content": user_input})

        # -----------------------------
        # CLEAN DISPLAY
        # -----------------------------
        def clean_list(lst):
            return " / ".join(list(set(lst))) if lst else "aucune"

        answer = f"""
🏥 ICU FLOW V4 - {st.session_state.current_patient}

🎯 CIBLE PRINCIPALE : {main_target}
🔁 CIBLES SECONDAIRES : {clean_list(secondary_targets)}

🫀 HÉMODYNAMIQUE : {clean_list(p['cibles']['hemodynamique'][-3:])}
🫁 RESPIRATOIRE : {clean_list(p['cibles']['respiratoire'][-3:])}
🧠 NEURO : {clean_list(p['cibles']['neuro'][-3:])}
🧪 RÉNAL : {clean_list(p['cibles']['renal'][-3:])}
🦠 INFECTIEUX : {clean_list(p['cibles']['infectieux'][-3:])}

🚨 RISQUES :
- {clean_list(risks)}

📝 NOTES :
- {clean_list(p['notes'][-3:])}

👉 FLOW V4 intelligent actif
"""

        with st.chat_message("assistant"):
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

        if mode == "QUICK ICU":

            answer = f"""
⚡ QUICK ICU

💊 Médicament : {user_input}

📦 Données :
{context if context else "non documenté"}

👉 Action : surveillance clinique
"""

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

                answer = f"💉 PERFUSION ICU REAL\n👉 {round(ml_h,2)} mL/h"
            else:
                answer = "médicament non reconnu"

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
