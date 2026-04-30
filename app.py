import streamlit as st

from core_flow import icu_flow_v2
from assist import icu_assist
from checklist import checklist_v2
from perfusion import display_perfusion

from patient_store import create_patient, get_patient, update_patient


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU ENGINE V4", layout="wide")
st.title("🏥 ICU ENGINE V4 — DUAL MODE")

# =========================================================
# MODE GLOBAL
# =========================================================
mode = st.sidebar.selectbox(
    "Mode",
    ["ICU FLOW", "ICU ASSIST", "CHECKLIST", "PERFUSION"]
)

patient_mode = st.sidebar.toggle("🧾 Mode patient actif")

patient_id = None

# =========================================================
# PATIENT SELECTION
# =========================================================
if patient_mode:
    st.sidebar.markdown("## 🧾 Patient")

    new_patient = st.sidebar.checkbox("Créer nouveau patient")

    if new_patient:
        st.info("Mode création patient actif")

    patient_id = st.sidebar.text_input("Patient ID (si existant)")


# =========================================================
# INPUT
# =========================================================
text = st.chat_input("Entrée clinique ICU...")


# =========================================================
# CREATE PATIENT
# =========================================================
if text and patient_mode and not patient_id:
    patient_id = create_patient(text)
    st.success(f"🧾 Patient créé : {patient_id}")


# =========================================================
# LOAD PATIENT
# =========================================================
patient = get_patient(patient_id) if patient_id else None


# =========================================================
# FLOW MODE
# =========================================================
if mode == "ICU FLOW" and text:

    if patient_mode and patient:
        context = "\n".join(patient["events"])
        flow = icu_flow_v2(text + " " + context)
    else:
        flow = icu_flow_v2(text)

    st.json(flow)

    if patient_id:
        update_patient(patient_id, text, flow=flow)


# =========================================================
# ASSIST MODE
# =========================================================
elif mode == "ICU ASSIST" and text:

    if patient_mode and patient:
        context = "\n".join(patient["events"])
        flow = icu_flow_v2(text + " " + context)
    else:
        flow = icu_flow_v2(text)

    assist = icu_assist(text, flow)

    st.json(assist)

    if patient_id:
        update_patient(patient_id, text, flow=flow, assist=assist)


# =========================================================
# CHECKLIST MODE
# =========================================================
elif mode == "CHECKLIST" and text:

    flow = icu_flow_v2(text)
    checklist = checklist_v2(flow, text)

    st.write(checklist)


# =========================================================
# PERFUSION MODE
# =========================================================
elif mode == "PERFUSION" and text:

    display_perfusion(st, text, 70)


# =========================================================
# PATIENT VIEW
# =========================================================
if patient_mode and patient:
    st.sidebar.markdown("## 📊 Patient data")

    st.sidebar.write("Events:")
    for e in patient["events"]:
        st.sidebar.write("•", e)

    if patient["last_flow"]:
        st.sidebar.markdown("### 🧠 Dernier FLOW")
        st.sidebar.json(patient["last_flow"])

    if patient["last_assist"]:
        st.sidebar.markdown("### ⚡ Dernier ASSIST")
        st.sidebar.json(patient["last_assist"])
