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
# FLOW MODE — VERSION CRITICAL CARE TRANSMISSION
# =========================================================
if mode == "ICU FLOW" and text:

    flow = icu_flow_v2(text)
    assist = icu_assist(text, flow)

    # =====================================================
    # 🧑‍⚕️ IDENTIFICATION / CONTEXTE
    # =====================================================
    st.markdown("## 🧑‍⚕️ IDENTIFICATION / CONTEXTE")
    st.info(flow.get("summary", "Pas de synthèse disponible"))

    st.divider()

    # =====================================================
    # 🔴 SYNTHÈSE CRITIQUE
    # =====================================================
    st.markdown("## 🔴 SYNTHÈSE CRITIQUE")

    st.markdown(f"**Gravité :** {flow.get('severity', 'N/A')}")
    st.markdown("**Défaillances suspectées :**")

    scores = flow.get("scores", {})

    for k, v in scores.items():
        try:
            if v >= 2:
                st.write(f"• {k.upper()} : atteinte significative")
        except:
            pass

    st.divider()

    # =====================================================
    # 🫁 RESPIRATOIRE
    # =====================================================
    st.markdown("## 🫁 RESPIRATOIRE")
    st.write("• Évaluation basée sur données disponibles")
    st.write(f"• Score : {scores.get('resp', 'N/A')}")

    st.divider()

    # =====================================================
    # ❤️ HÉMODYNAMIQUE
    # =====================================================
    st.markdown("## ❤️ HÉMODYNAMIQUE")
    st.write(f"• Score : {scores.get('hemo', 'N/A')}")
    st.write("• Surveillance PAM, FC, perfusion périphérique")

    st.divider()

    # =====================================================
    # 🧠 NEUROLOGIQUE
    # =====================================================
    st.markdown("## 🧠 NEUROLOGIQUE")
    st.write(f"• Score : {scores.get('neuro', 'N/A')}")
    st.write("• Interprétation à adapter si sédation")

    st.divider()

    # =====================================================
    # 💧 RÉNAL / MÉTABOLIQUE
    # =====================================================
    st.markdown("## 💧 RÉNAL / MÉTABOLIQUE")
    st.write(f"• Score : {scores.get('metab', 'N/A')}")
    st.write("• Surveillance diurèse, créatinine, ionogramme")

    st.divider()

    # =====================================================
    # 🦠 INFECTIEUX
    # =====================================================
    st.markdown("## 🦠 INFECTIEUX")
    st.write(f"• Score : {scores.get('infect', 'N/A')}")
    st.write("• Recherche de foyer + adaptation ATB")

    st.divider()

    # =====================================================
    # 🎯 OBJECTIFS THÉRAPEUTIQUES
    # =====================================================
    st.markdown("## 🎯 OBJECTIFS THÉRAPEUTIQUES")

    for t in flow.get("targets", []):
        st.write(f"• {t}")

    st.divider()

    # =====================================================
    # ⚠️ POINTS CRITIQUES
    # =====================================================
    st.markdown("## ⚠️ POINTS CRITIQUES")

    for a in assist.get("actions", []):
        st.write(f"• {a}")

    st.divider()

    # =====================================================
    # 📋 TRANSMISSION ICU STRUCTURÉE
    # =====================================================
    st.markdown("## 📋 TRANSMISSION ICU")

    sbar = assist.get("sbar", {})

    st.info(f"""
**IDENTIFICATION :** Patient en réanimation  

**SITUATION :** {sbar.get('S', 'N/A')}  

**CONTEXTE :** {sbar.get('B', 'N/A')}  

**ÉVALUATION :** {sbar.get('A', 'N/A')}  

**PLAN / RECOMMANDATIONS :** {sbar.get('R', 'N/A')}
""")

    # =====================================================
    # PATIENT UPDATE
    # =====================================================
    if patient_id:
        update_patient(patient_id, text, flow=flow, assist=assist)


# =========================================================
# ASSIST MODE (INCHANGÉ)
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
# CHECKLIST MODE (INCHANGÉ)
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
# PERFUSION MODE (INCHANGÉ)
# =========================================================
elif mode == "PERFUSION" and text:

    st.markdown("## 💉 PERFUSION ICU")

    display_perfusion(st, text, 70)


# =========================================================
# PATIENT SIDEBAR (INCHANGÉ)
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
