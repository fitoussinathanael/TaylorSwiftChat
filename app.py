# =========================================================
# ICU ENGINE V2 — APP.PY FINAL (STABLE RÉA)
# FLOW + ASSIST + CHECKLIST + PERFUSION
# =========================================================

import streamlit as st
import re

from core_flow import icu_flow_v2
from assist import icu_assist
from checklist import checklist_v2
from perfusion import display_perfusion
from pharmaco import detect_drug

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V2", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V2 — RÉANIMATION")

st.caption("FLOW · ASSIST · CHECKLIST · PERFUSION — SYSTÈME CLINIQUE STRUCTURÉ")

# =========================================================
# MODE
# =========================================================
mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "ICU ASSIST", "CHECKLIST PLATEAU", "PERFUSION ICU"]
)

# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Entrée clinique ICU...")

# =========================================================
# HELPERS
# =========================================================
def extract_weight(text):
    w = re.findall(r'(\d{2,3})', text)
    return int(w[0]) if w else None


# =========================================================
# UI MODE HELPERS
# =========================================================
def show_example(text):
    st.markdown(f"*Exemple : {text}*")


# =========================================================
# ICU FLOW
# =========================================================
if mode == "ICU FLOW":

    st.subheader("🧠 ICU FLOW — Analyse clinique structurée")
    show_example("dyspnée + fièvre + sat 86% sous 6L O2 + TA 90/50 + confusion")

    if user_input:
        flow = icu_flow_v2(user_input)

        st.markdown("### 🎯 CIBLES")
        for t in flow["targets"]:
            st.write("•", t)

        st.markdown(f"### ⚠️ GRAVITÉ : {flow['severity']}")

        st.markdown("### 📊 SCORES")
        st.json(flow["scores"])

        st.markdown("### 📝 NOTE CLINIQUE")
        st.text(flow["note"])

        st.markdown("### 📋 TRANSMISSION SBAR")
        st.json(flow["sbar"])


# =========================================================
# ICU ASSIST
# =========================================================
elif mode == "ICU ASSIST":

    st.subheader("🧠 ICU ASSIST — Priorisation clinique")
    show_example("même input que FLOW : dyspnée + choc + fièvre")

    if user_input:
        flow = icu_flow_v2(user_input)
        assist = icu_assist(user_input, flow)

        st.markdown(f"### 🚨 PRIORITÉ : {assist['priority']}")

        st.markdown("### 🧠 SYNTHÈSE")
        st.write(assist["summary"])

        st.markdown("### ⚡ ACTIONS PRIORITAIRES")
        for a in assist["actions"]:
            st.write("•", a)

        if assist["warnings"]:
            st.markdown("### ⚠️ ALERTES")
            for w in assist["warnings"]:
                st.warning(w)

        if assist["pharmaco_flags"]:
            st.markdown("### 💉 PHARMACO")
            for p in assist["pharmaco_flags"]:
                st.info(p)

        st.markdown("### 📋 SBAR")
        st.json(assist["sbar"])


# =========================================================
# CHECKLIST
# =========================================================
elif mode == "CHECKLIST PLATEAU":

    st.subheader("📋 CHECKLIST PLATEAU — Préparation terrain")
    show_example("intubation + hypoxie + choc + sepsis")

    if user_input:
        flow = icu_flow_v2(user_input)
        checklist = checklist_v2(flow, user_input)

        for section, items in checklist:
            st.markdown(f"## {section}")
            for i in items:
                st.write(i)


# =========================================================
# PERFUSION ICU
# =========================================================
elif mode == "PERFUSION ICU":

    st.subheader("💉 PERFUSION ICU — Calcul doses réa")
    show_example("noradrenaline 70 kg ou propofol 80 kg")

    if user_input:

        drug = detect_drug(user_input)
        weight = extract_weight(user_input)

        if drug and weight:
            display_perfusion(st, drug, weight)
        else:
            st.error("💉 Format attendu : médicament + poids (ex: noradrenaline 70 kg)")
