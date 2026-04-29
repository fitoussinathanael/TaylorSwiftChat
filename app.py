import streamlit as st
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V8", page_icon="🏥", layout="wide")

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
# UI
# =========================================================
st.title("🏥 ICU Engine V8 - FLOW PRO (STABLE)")

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
        "notes": [],
        "risques": []
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


# RESET
if st.sidebar.button("Reset session"):
    st.session_state.messages = []
    st.rerun()


# =========================================================
# DISPLAY HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Entrée ICU...")


# =========================================================
# ICU FLOW ENGINE V8
# =========================================================
def add_unique(lst, item):
    if item and item not in lst:
        lst.append(item)


def clean(lst, n=3):
    return " / ".join(lst[-n:]) if lst else "aucune"


def detect_engine(text):
    """simple scoring engine"""
    score = {
        "hemodynamique": 0,
        "respiratoire": 0,
        "neuro": 0,
        "renal": 0,
        "infectieux": 0
    }

    risks = []

    # HEMO
    if any(x in text for x in ["norad", "nora", "tension", "hypotension"]):
        score["hemodynamique"] += 2
    if "norad" in text or "nora" in text:
        risks.append("instabilité hémodynamique")

    # NEURO
    if "propof" in text:
        score["neuro"] += 2
        risks.append("sédation + hypotension")
    if "midaz" in text:
        score["neuro"] += 1

    # RESP
    if any(x in text for x in ["ventil", "intub"]):
        score["respiratoire"] += 2
    if "fenta" in text:
        risks.append("dépression respiratoire")

    # RENAL
    if any(x in text for x in ["creat", "diurese"]):
        score["renal"] += 1

    # INFECT
    if any(x in text for x in ["sepsis", "infection"]):
        score["infectieux"] += 3
        risks.append("risque choc septique")

    return score, risks


# =========================================================
# FLOW MODE
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        patient = st.session_state.patients[st.session_state.current_patient]
        text = user_input.lower()

        scores, risks = detect_engine(text)

        # -------------------------
        # ROUTING MEMORY
        # -------------------------
        mapping = {
            "hemodynamique": ["norad", "nora", "tension", "hypotension"],
            "respiratoire": ["ventil", "intub", "fenta"],
            "neuro": ["propof", "midaz"],
            "renal": ["creat", "diurese"],
            "infectieux": ["sepsis", "infection"]
        }

        routed = False

        for key, keywords in mapping.items():
            if any(k in text for k in keywords):
                add_unique(patient["cibles"][key], user_input)
                routed = True

        if not routed:
            patient["notes"].append(user_input)

        # -------------------------
        # PRIORITY TARGETS
        # -------------------------
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        main_target = sorted_scores[0][0] if sorted_scores else "aucune"
        secondary = [k for k, v in sorted_scores[1:] if v > 0]

        # -------------------------
        # STORE MESSAGE
        # -------------------------
        st.session_state.messages.append({"role": "user", "content": user_input})

        # -------------------------
        # OUTPUT CLEAN (IMPORTANT)
        # -------------------------
        answer = f"""
🏥 ICU FLOW V8 - {st.session_state.current_patient}

🎯 CIBLE PRINCIPALE : {main_target}
🔁 SECONDAIRES : {", ".join(secondary) if secondary else "aucune"}

---

🫀 HÉMODYNAMIQUE : {clean(patient["cibles"]["hemodynamique"])}
🫁 RESPIRATOIRE : {clean(patient["cibles"]["respiratoire"])}
🧠 NEURO : {clean(patient["cibles"]["neuro"])}
🧪 RÉNAL : {clean(patient["cibles"]["renal"])}
🦠 INFECTIEUX : {clean(patient["cibles"]["infectieux"])}

---

🚨 RISQUES PRIORITAIRES :
- {chr(10).join("🔴 " + r for r in risks[:2]) if risks else "aucun détecté"}

---

📝 NOTES :
- {clean(patient["notes"])}

👉 FLOW V8 ACTIVE (STABLE + CLEAN)
"""

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

# =========================================================
# CLASSIC MODES (LIGHT CLEAN)
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
            answer = "💉 PERFUSION ICU REAL (stable mode)"

        elif mode == "PERFUSION TERRAIN":
            answer = "🏥 PERFUSION TERRAIN (stable mode)"

        else:
            answer = f"🧠 IA ICU\n\n{user_input}\n\n{context}"

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
