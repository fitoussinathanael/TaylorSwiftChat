import streamlit as st
from perfusion_engine import perfusion_response

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V11", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V11")
st.caption("FLOW · PERFUSION · CHECKLIST · QUICK ICU")

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
    ["ICU FLOW", "PERFUSION ICU", "CHECKLIST PLATEAU", "QUICK ICU"]
)

# =========================================================
# PATIENT MANAGEMENT (FLOW ONLY)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {"notes": []}
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHAT DISPLAY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# ICU FLOW (simple et stable)
# =========================================================
def icu_flow(text):
    t = text.lower()

    targets = []
    if any(x in t for x in ["dysp", "hypox", "sat", "o2"]):
        targets.append("🫁 Respiratoire")
    if any(x in t for x in ["choc", "hypotension", "norad"]):
        targets.append("🫀 Hémodynamique")
    if any(x in t for x in ["sepsis", "infection", "fièvre"]):
        targets.append("🦠 Infectieux")

    severity = "🟡 MODÉRÉ"
    if "hypox" in t and "choc" in t:
        severity = "🔴 CRITIQUE"
    elif "hypox" in t or "choc" in t:
        severity = "🟠 SÉVÈRE"

    return f"""
🧠 ICU FLOW

🎯 CIBLES : {" | ".join(targets) if targets else "Non précisées"}

⚠️ GRAVITÉ : {severity}

📝 INPUT :
{text}
"""

# =========================================================
# CHECKLIST DYNAMIQUE
# =========================================================
def checklist(text):
    t = text.lower()

    if "intubation" not in t:
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    hypox = any(x in t for x in ["hypox", "sat", "dysp"])
    choc = any(x in t for x in ["choc", "hypotension"])
    sepsis = any(x in t for x in ["sepsis", "infection", "fièvre"])

    base = """
📋 CHECKLIST INTUBATION

🔧 MATÉRIEL
☐ Laryngoscope
☐ Sonde
☐ Capno
☐ Aspiration
"""

    if hypox:
        base += "\n🫁 HYPOXIE\n☐ Pré-oxygénation\n☐ PEEP\n"

    if choc:
        base += "\n🫀 CHOC\n☐ Noradrénaline prête\n☐ VVP OK\n"

    if sepsis:
        base += "\n🦠 SEPSIS\n☐ ATB\n☐ Lactates\n"

    base += "\n🧠 STRATÉGIE\n☐ Plan A/B/C\n☐ Équipe prête\n"

    return base

# =========================================================
# QUICK ICU (fallback simple)
# =========================================================
def quick_icu(text):
    return f"""
⚡ QUICK ICU

📝 Input :
{text}

👉 Utiliser FLOW ou PERFUSION pour analyse détaillée
"""

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------
    # MODE FLOW
    # -------------------------
    if mode == "ICU FLOW":
        answer = icu_flow(user_input)

    # -------------------------
    # MODE PERFUSION
    # -------------------------
    elif mode == "PERFUSION ICU":
        answer = perfusion_response(user_input)

    # -------------------------
    # MODE CHECKLIST
    # -------------------------
    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    # -------------------------
    # MODE QUICK
    # -------------------------
    elif mode == "QUICK ICU":
        answer = quick_icu(user_input)

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
