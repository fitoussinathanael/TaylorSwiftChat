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

st.title("🏥 ICU ENGINE V4 — RÉANIMATION")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "ICU ASSIST", "CHECKLIST", "PERFUSION"]
)

patient_mode = st.sidebar.toggle("🧾 Mode patient actif")

patient_id = st.sidebar.text_input("Patient ID (optionnel)")

text = st.chat_input("Entrée clinique ICU...")


# =========================================================
# PATIENT CREATE
# =========================================================
if text and patient_mode and not patient_id:
    patient_id = create_patient(text)
    st.sidebar.success(f"🧾 Patient créé : {patient_id}")


patient = get_patient(patient_id) if patient_id else None


# =========================================================
# FLOW MODE
# =========================================================
if mode == "ICU FLOW" and text:

    flow = icu_flow_v2(text)
    assist = icu_assist(text, flow)

    # =====================================================
    # 🚨 GRAVITÉ
    # =====================================================
    st.markdown("## 🚨 GRAVITÉ")
    st.markdown(f"# {flow['severity']}")

    st.divider()

    # =====================================================
    # 🎯 CIBLES
    # =====================================================
    st.markdown("## 🎯 CIBLES PRIORITAIRES")

    for t in flow["targets"]:
        st.write(f"• {t}")

    st.divider()

    # =====================================================
    # 🧠 SYNTHÈSE
    # =====================================================
    st.markdown("## 🧠 SYNTHÈSE CLINIQUE")

    st.success(flow["summary"])

    st.divider()

    # =====================================================
    # 📊 SCORES (MONITOR STYLE)
    # =====================================================
    st.markdown("## 📊 SCORES ORGANIQUES")

    cols = st.columns(5)

    labels = ["RESP 🫁", "HEMO 🫀", "INFECT 🦠", "NEURO 🧠", "METAB ⚗️"]
    keys = ["resp", "hemo", "infect", "neuro", "metab"]

    for i in range(5):
        cols[i].metric(labels[i], flow["scores"][keys[i]])

    st.divider()

    # =====================================================
    # ⚡ ACTIONS
    # =====================================================
    st.markdown("## ⚡ ACTIONS IMMÉDIATES")

    for a in assist["actions"]:
        st.markdown(f"- ⚡ {a}")

    st.divider()

    # =====================================================
    # 📋 SBAR
    # =====================================================
    st.markdown("## 📋 TRANSMISSION SBAR")

    sbar = assist["sbar"]

    st.info(f"""
**S** : {sbar['S']}  
**B** : {sbar['B']}  
**A** : {sbar['A']}  
**R** : {sbar['R']}
""")

    # =====================================================
    # PATIENT UPDATE
    # =====================================================
    if patient_id:
        update_patient(patient_id, text, flow=flow, assist=assist)


# =========================================================
# ASSIST MODE
# =========================================================
elif mode == "ICU ASSIST" and text:

    flow = icu_flow_v2(text)
    assist = icu_assist(text, flow)

    st.markdown("## 🧠 PRIORITÉ")

    if "🔴" in assist["priority"]:
        st.error(assist["priority"])
    else:
        st.warning(assist["priority"])

    st.divider()

    st.markdown("## 🧠 SYNTHÈSE")
    st.write(assist["summary"])

    st.divider()

    st.markdown("## ⚡ ACTIONS")

    for a in assist["actions"]:
        st.write(f"• {a}")

    st.divider()

    st.markdown("## 📋 SBAR")

    st.json(assist["sbar"])


# =========================================================
# CHECKLIST MODE
# =========================================================
elif mode == "CHECKLIST" and text:

    flow = icu_flow_v2(text)
    checklist = checklist_v2(flow, text)

    st.markdown("## 📋 CHECKLIST PLATEAU")

    for section, items in checklist:
        st.subheader(section)
        for i in items:
            st.write(f"☐ {i}")


# =========================================================
# PERFUSION MODE
# =========================================================
elif mode == "PERFUSION" and text:

    st.markdown("## 💉 PERFUSION ICU")

    display_perfusion(st, text, 70)


# =========================================================
# PATIENT SIDEBAR
# =========================================================
if patient_mode and patient:

    st.sidebar.markdown("## 🧾 PATIENT")

    st.sidebar.markdown("### 📌 HISTORIQUE")

    for e in patient["events"]:
        st.sidebar.write("•", e)

    if patient["last_flow"]:
        st.sidebar.markdown("### 🧠 DERNIER FLOW")
        st.sidebar.json(patient["last_flow"])

    if patient["last_assist"]:
        st.sidebar.markdown("### ⚡ DERNIER ASSIST")
        st.sidebar.json(patient["last_assist"])
