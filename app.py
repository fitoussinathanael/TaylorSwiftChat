import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V10", page_icon="🏥")

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
st.title("🏥 ICU Engine V10 - FLOW V6 (STABLE)")

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
# ICU FLOW V6 (CLEAN + STABLE)
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        p = st.session_state.patients[st.session_state.current_patient]
        text = user_input.lower()

        risks = []
        fragments = {
            "hemodynamique": [],
            "respiratoire": [],
            "neuro": [],
            "renal": [],
            "infectieux": []
        }

        # -----------------------------
        # CLINICAL EXTRACTION
        # -----------------------------
        if "norad" in text or "nora" in text:
            fragments["hemodynamique"].append("vasopresseur (norad)")
            risks.append("instabilité hémodynamique")

        if "hypotension" in text:
            fragments["hemodynamique"].append("hypotension")

        if "propof" in text:
            fragments["neuro"].append("propofol")
            risks.append("sédation + hypotension")

        if "midaz" in text:
            fragments["neuro"].append("midazolam")

        if "fenta" in text:
            fragments["respiratoire"].append("opioïde")
            risks.append("dépression respiratoire")

        if "intub" in text or "ventil" in text:
            fragments["respiratoire"].append("ventilation mécanique")

        if "creat" in text or "diurese" in text:
            fragments["renal"].append("fonction rénale altérée")

        if "sepsis" in text or "infection" in text:
            fragments["infectieux"].append("sepsis suspect")
            risks.append("risque choc septique")

        # -----------------------------
        # MEMORY UPDATE (SAFE)
        # -----------------------------
        for k in fragments:
            for item in fragments[k]:
                if item not in p["cibles"][k]:
                    p["cibles"][k].append(item)

        if not any(fragments.values()):
            p["notes"].append(user_input)

        # -----------------------------
        # PRIORITY SCORING (FIXED)
        # -----------------------------
        scores = {k: len(v) for k, v in fragments.items()}

        if sum(scores.values()) == 0:
            main_target = "aucune"
            secondary = []
        else:
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            main_target = sorted_scores[0][0]
            secondary = [k for k, v in sorted_scores[1:] if v > 0]

        # -----------------------------
        # CLEAN DISPLAY
        # -----------------------------
        def clean(lst):
            return " / ".join(lst[-3:]) if lst else "aucune"

        answer = f"""
🏥 ICU FLOW V6 - {st.session_state.current_patient}

🎯 CIBLE PRINCIPALE : {main_target}
🔁 SECONDAIRES : {clean(secondary)}

🫀 HÉMODYNAMIQUE : {clean(p['cibles']['hemodynamique'])}
🫁 RESPIRATOIRE : {clean(p['cibles']['respiratoire'])}
🧠 NEURO : {clean(p['cibles']['neuro'])}
🧪 RÉNAL : {clean(p['cibles']['renal'])}
🦠 INFECTIEUX : {clean(p['cibles']['infectieux'])}

🚨 RISQUES :
- { " / ".join(risks) if risks else "aucun détecté" }

📝 NOTES :
- {clean(p['notes'])}

👉 FLOW V6 stable actif
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
