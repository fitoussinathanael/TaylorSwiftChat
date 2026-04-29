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
    st.sidebar.markdown("## 💉 Perfusion ICU")
    st.sidebar.info(
        "Tape : nom du médicament + poids patient\n\n"
        "Ex : `noradrénaline 70kg`\n"
    )

elif mode == "CHECKLIST PLATEAU":
    st.sidebar.markdown("## 📋 Checklist Plateau")
    st.sidebar.info("Tape le nom de la procédure")

elif mode == "IA CLINIQUE":
    st.sidebar.markdown("## 🧠 IA Clinique")

elif mode == "QUICK ICU":
    st.sidebar.markdown("## ⚡ Quick ICU")

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
# PERFUSION ENGINE SAFE FIX
# =========================================================

def safe_strip(x):
    return str(x or "")

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ─────────────────────────────────────────────
    # QUICK ICU FIX
    # ─────────────────────────────────────────────
    if mode == "QUICK ICU":
        context = search_icu(user_input)
        if not context:
            context = "Aucun résultat dans la base documentaire."

        answer = f"""⚡ QUICK ICU

{context}

👉 ICU ENGINE V10.2"""

    # ─────────────────────────────────────────────
    # PERFUSION ICU SAFE FIX
    # ─────────────────────────────────────────────
    elif mode == "PERFUSION ICU":
        drug_name, weight = detect_drug_and_weight(user_input)

        if not drug_name:
            answer = "💉 Médicament non reconnu"
        elif not weight:
            answer = f"💉 Poids manquant pour {drug_name}"
        else:
            drug_data = CONCENTRATIONS[drug_name]
            rag_context = safe_strip(search_icu(drug_data["fiche_rag"]))
            answer = format_perfusion_answer(drug_name, weight, drug_data, rag_context)

    # ─────────────────────────────────────────────
    # CHECKLIST
    # ─────────────────────────────────────────────
    elif mode == "CHECKLIST PLATEAU":
        proc = detect_procedure(user_input)
        if proc and proc in CHECKLISTS:
            answer = format_checklist(proc, CHECKLISTS[proc])
        else:
            answer = "Procédure non reconnue"

    # ─────────────────────────────────────────────
    # IA CLINIQUE SAFE RAG FIX
    # ─────────────────────────────────────────────
    elif mode == "IA CLINIQUE":
        rag_context = safe_strip(search_icu(user_input))
        answer = format_ia_clinique(user_input, rag_context)

    # ─────────────────────────────────────────────
    # ICU FLOW (inchangé)
    # ─────────────────────────────────────────────
    elif mode == "ICU FLOW":
        if not st.session_state.current_patient:
            st.warning("Aucun patient")
            st.stop()

        patient = st.session_state.patients[st.session_state.current_patient]

        extracted = extract_clinical(user_input)
        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]:
                    patient["cibles"][k].append(item)

        new_numerics = extract_numerics(user_input)
        update_numerics(patient, new_numerics)

        flags = compute_flags(user_input, patient["cibles"])
        num_analysis = analyze_numerics(patient)
        pam_level = detect_pam_risk(user_input, flags, num_analysis)

        main_problem = build_main_problem(flags, pam_level, num_analysis)
        action_prio = build_action_prioritaire(flags, pam_level, num_analysis)
        critique, important, surveillance = build_monitor_alerts_fused(flags, pam_level, num_analysis)
        evolution = build_evolution(flags, pam_level, num_analysis)
        actions = build_actions_secondaires(flags, pam_level, num_analysis)
        numeric_panel = build_numeric_panel(patient, num_analysis)

        answer = format_icu_flow(
            main_problem, action_prio,
            critique, important, surveillance,
            evolution, actions, numeric_panel
        )

    else:
        answer = "Mode non reconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
