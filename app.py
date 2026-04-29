import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(page_title="ICU Engine V10.4 PRO", page_icon="🏥", layout="wide")

# CSS terrain : haute lisibilité, alertes visibles, typographie claire
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    h1 { color: #58a6ff !important; font-family: 'Courier New', monospace !important; }

    .alert-critique {
        background: #3d0000; border-left: 5px solid #ff4444;
        padding: 12px 16px; border-radius: 6px; font-weight: bold;
        font-size: 1.1em; color: #ff8888; margin: 8px 0;
    }
    .alert-severe {
        background: #2d1800; border-left: 5px solid #ff8c00;
        padding: 12px 16px; border-radius: 6px; font-weight: bold;
        color: #ffb347; margin: 8px 0;
    }
    .alert-modere {
        background: #1a1a00; border-left: 5px solid #ffd700;
        padding: 12px 16px; border-radius: 6px;
        color: #ffd700; margin: 8px 0;
    }
    .alert-ok {
        background: #001a00; border-left: 5px solid #00cc44;
        padding: 12px 16px; border-radius: 6px;
        color: #44ff88; margin: 8px 0;
    }

    .sbar-block {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 14px 18px; margin: 6px 0;
    }
    .sbar-label {
        color: #58a6ff; font-weight: bold; font-size: 0.85em;
        text-transform: uppercase; letter-spacing: 1px;
    }

    .score-badge {
        display: inline-block; padding: 4px 12px;
        border-radius: 20px; font-weight: bold; font-size: 0.9em;
        margin: 2px;
    }
    .badge-red { background: #3d0000; color: #ff4444; border: 1px solid #ff4444; }
    .badge-orange { background: #2d1800; color: #ff8c00; border: 1px solid #ff8c00; }
    .badge-yellow { background: #1a1a00; color: #ffd700; border: 1px solid #ffd700; }
    .badge-green { background: #001a00; color: #44ff88; border: 1px solid #44ff88; }
    .badge-blue { background: #001933; color: #58a6ff; border: 1px solid #58a6ff; }

    [data-testid="stChatMessage"] {
        background: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    .stTextInput input {
        background: #21262d !important;
        color: #e6edf3 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 ICU ENGINE V10.4 PRO")
st.caption("ICU FLOW · PERFUSION · CHECKLIST · QUICK ICU · RAG ICU")

# =========================================================
# SESSION STATE
# =========================================================

for key, default in [
    ("messages", []),
    ("patients", {}),
    ("current_patient", None),
    ("checklist_states", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================
# MODE
# =========================================================

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU"]
)

# =========================================================
# PATIENT
# =========================================================

if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter") and new_patient.strip():
        name = new_patient.strip()
        st.session_state.patients[name] = {"notes": []}
        st.session_state.current_patient = name
        st.sidebar.success(f"✅ {name}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# UTILS
# =========================================================

def safe_rag(query: str):
    if not query:
        return None
    try:
        res = search_icu(query)
        return res if isinstance(res, dict) else None
    except:
        return None


def compute_map(sys, dia):
    return round((sys + 2 * dia) / 3, 1)


def extract_bp(text):
    match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

# =========================================================
# ICU FLOW
# (inchangé logique, seulement safe syntax)
# =========================================================

def build_flow(text):
    t = text.lower()

    resp_score = 0
    if "dysp" in t: resp_score += 1
    if "hypox" in t or "84%" in t or "85%" in t: resp_score += 2

    shock_score = 0
    sys_val, dia_val = extract_bp(text)
    if sys_val and sys_val < 90: shock_score += 3
    if "ta" in t or "hypotension" in t: shock_score += 2

    severity = "CRITIQUE" if resp_score + shock_score >= 4 else "SÉVÈRE"

    pam = None
    if sys_val and dia_val:
        pam = compute_map(sys_val, dia_val)

    return f"""
ICU FLOW OK
RESP: {resp_score}
CHOC: {shock_score}
SEVERITE: {severity}
PAM: {pam}
"""

# =========================================================
# QUICK ICU
# =========================================================

def quick(text):
    rag = safe_rag(text)
    if not rag:
        return "NO RAG"
    return str(rag)

# =========================================================
# CHECKLIST SIMPLE
# =========================================================

def checklist(text):
    return "📋 CHECKLIST INTUBATION\n☐ matériel ☐ médicaments ☐ vérifications"

# =========================================================
# CHAT
# =========================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if mode == "ICU FLOW":
        answer = build_flow(user_input)
    elif mode == "QUICK ICU":
        answer = quick(user_input)
    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)
    else:
        answer = "MODE OK"

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)
