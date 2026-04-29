import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V11", page_icon="🏥")

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
st.title("🏥 ICU Engine V11 - FLOW V7 (PRO PRIORITY)")

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
    if new_patient not in st.session_state.patients:

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
    st.success(f"Patient actif : {new_patient}")

patient_list = list(st.session_state.patients.keys())

if patient_list:
    try:
        index = patient_list.index(st.session_state.current_patient)
    except:
        index = 0
        st.session_state.current_patient = patient_list[0]

    selected = st.sidebar.selectbox(
        "Patient actif",
        patient_list,
        index=index
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
# ICU FLOW V7 (PRIORITY + ACTION ENGINE)
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        p = st.session_state.patients[st.session_state.current_patient]
        text = user_input.lower()

        risks = []
        actions = []

        fragments = {
            "hemodynamique": [],
            "respiratoire": [],
            "neuro": [],
            "renal": [],
            "infectieux": []
        }

        # -----------------------------
        # CLINICAL DETECTION
        # -----------------------------
        if "norad" in text or "nora" in text:
            fragments["hemodynamique"].append("vasopresseur (norad)")
            risks.append(("instabilité hémodynamique", "🔴"))
            actions.append("adapter noradrénaline + surveillance TA invasive")

        if "hypotension" in text:
            fragments["hemodynamique"].append("hypotension")

        if "propof" in text:
            fragments["neuro"].append("propofol")
            risks.append(("sédation + hypotension", "🟠"))
            actions.append("réévaluer profondeur sédation")

        if "midaz" in text:
            fragments["neuro"].append("midazolam")

        if "fenta" in text:
            fragments["respiratoire"].append("opioïde")
            risks.append(("dépression respiratoire", "🟠"))

        if "ventil" in text or "intub" in text:
            fragments["respiratoire"].append("ventilation mécanique")

        if "creat" in text or "diurese" in text:
            fragments["renal"].append("altération rénale possible")

        if "sepsis" in text or "infection" in text:
            fragments["infectieux"].append("sepsis suspect")
            risks.append(("risque choc septique", "🔴"))
            actions.append("rechercher foyer infectieux + antibiothérapie")

        # -----------------------------
        # MEMORY UPDATE
        # -----------------------------
        for k in fragments:
            for item in fragments[k]:
                if item not in p["cibles"][k]:
                    p["cibles"][k].append(item)

        if not any(fragments.values()):
            p["notes"].append(user_input)

        # -----------------------------
        # PRIORITY ENGINE
        # -----------------------------
        def priority_label(r):
            if r[1] == "🔴":
                return 3
            if r[1] == "🟠":
                return 2
            return 1

        risks_sorted = sorted(risks, key=priority_label, reverse=True)

        # -----------------------------
        # CLEAN DISPLAY
        # -----------------------------
        def clean(lst):
            return " / ".join(lst[-3:]) if lst else "aucune"

        def format_risks(r):
            if not r:
                return "aucun détecté"
            return "\n- ".join([f"{lvl} {txt}" for txt, lvl in r])

        def format_actions(a):
            return "\n- ".join(a[-4:]) if a else "surveillance standard"

        answer = f"""
🏥 ICU FLOW V7 - {st.session_state.current_patient}

🚨 RISQUES PRIORISÉS :
- {format_risks(risks_sorted)}

⚡ ACTIONS IMMÉDIATES :
- {format_actions(actions)}

🎯 CIBLES ACTIVES :
🫀 HÉMODYNAMIQUE : {clean(p['cibles']['hemodynamique'])}
🫁 RESPIRATOIRE : {clean(p['cibles']['respiratoire'])}
🧠 NEURO : {clean(p['cibles']['neuro'])}
🧪 RÉNAL : {clean(p['cibles']['renal'])}
🦠 INFECTIEUX : {clean(p['cibles']['infectieux'])}

📝 NOTES :
- {clean(p['notes'])}

👉 FLOW V7 PRIORITY ACTIVE
"""

        st.session_state.messages.append({"role": "user", "content": user_input})

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
