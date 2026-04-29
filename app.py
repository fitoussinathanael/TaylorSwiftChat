import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.6 PRO", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.6 PRO")
st.caption("ICU FLOW · QUICK ICU · PERFUSION MONITOR · CHECKLIST · RAG ICU")

# =========================================================
# STATE INIT
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patients" not in st.session_state:
    st.session_state.patients = {}

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

if "icu_cache" not in st.session_state:
    st.session_state.icu_cache = {}

if "dose_factor" not in st.session_state:
    st.session_state.dose_factor = 1.0


# =========================================================
# MODE
# =========================================================
mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU"]
)

# =========================================================
# PATIENT SYSTEM (FIX IMPORTANT)
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients ICU")

    new_patient = st.sidebar.text_input("Créer patient")

    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {
            "notes": [],
            "flow": None
        }
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    if st.session_state.patients:
        st.session_state.current_patient = st.sidebar.selectbox(
            "Patient actif",
            list(st.session_state.patients.keys())
        )

# =========================================================
# CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# SAFE RAG (CACHE)
# =========================================================
def safe_rag(query: str):
    if not query:
        return None

    if query in st.session_state.icu_cache:
        return st.session_state.icu_cache[query]

    try:
        res = search_icu(query)
        if isinstance(res, dict):
            st.session_state.icu_cache[query] = res
            return res
    except:
        pass

    return None


# =========================================================
# MAP
# =========================================================
def compute_map(text):
    match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not match:
        return None
    sys = int(match.group(1))
    dia = int(match.group(2))
    return round((sys + 2 * dia) / 3, 1)


# =========================================================
# ICU FLOW (STABLE)
# =========================================================
def build_flow(text):
    t = text.lower()

    resp = any(x in t for x in ["hypox", "dysp", "sat", "84%", "85%"])
    shock = any(x in t for x in ["choc", "norad", "85/50", "hypotension"])
    sepsis = any(x in t for x in ["fièvre", "sepsis", "infection", "pneumonie"])

    resp_score = 2 if resp else 0
    shock_score = 2 if shock else 0

    sofa = resp_score + shock_score

    severity = "🔴 CRITIQUE" if sofa >= 4 else "🟠 SÉVÈRE" if sofa >= 2 else "🟡 MODÉRÉ"

    # save patient flow
    if st.session_state.current_patient:
        st.session_state.patients[st.session_state.current_patient]["flow"] = {
            "text": text,
            "severity": severity
        }

    return f"""
🧠 ICU FLOW

📊 RESP : {resp_score} | CHOC : {shock_score} | SOFA : {sofa}
⚠️ GRAVITÉ : {severity}

🩺 PAM : {compute_map(text) or "N/A"} mmHg
"""


# =========================================================
# QUICK ICU (FIX IMPORTANT + FALLBACK INTELLIGENT)
# =========================================================
def quick(text):
    rag = safe_rag(text)

    if rag:
        return f"""
⚡ QUICK ICU

- Classe : {rag.get('classe','-')}
- Usage : {rag.get('usage','-')}
- Effets : {rag.get('effets','-')}
- Surveillance : {rag.get('surveillance','-')}
"""

    # fallback clinique intelligent
    t = text.lower()

    resp = "hypox" in t or "sat" in t
    shock = "ta" in t or "choc" in t
    sepsis = "fièvre" in t or "infection" in t

    targets = []
    if resp:
        targets.append("🫁 SpO2 > 92%")
    if shock:
        targets.append("🫀 PAM ≥ 65 mmHg")
    if sepsis:
        targets.append("🦠 ATB < 1h")

    return f"""
⚡ QUICK ICU — ANALYSE RÉA

🎯 CIBLES : {" | ".join(targets) if targets else "Surveillance clinique"}

⚠️ GRAVITÉ : 🟡 MODÉRÉ

🧠 ACTIONS :
- Stabilisation ABC
- Monitorage continu
- Réévaluation rapide

📝 INPUT : {text}
"""


# =========================================================
# PERFUSION (SAFE + STABLE)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "steps": [0.05, 0.1, 0.2, 0.5]},
    "propofol": {"conc": 10, "steps": [1, 2, 3, 4]},
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrenaline": "noradrenaline",
    "propofol": "propofol",
}

def detect_perf(text):
    t = text.lower()

    drug = None
    weight = None

    for k, v in ALIASES.items():
        if k in t:
            drug = v

    w = re.findall(r'(\d{2,3})\s*kg', t)
    if w:
        weight = int(w[0])

    return drug, weight


def calc(dose, weight, conc):
    return round(((dose * weight) / conc) * 2) / 2


def perfusion(drug, weight):
    d = DRUGS[drug]

    out = f"💉 {drug.upper()} — {weight} kg\n\n"
    out += "DOSE | RÉEL (mL/h)\n"
    out += "-------------------\n"

    for dose in d["steps"]:
        real = calc(dose, weight, d["conc"])
        out += f"{dose} | {real}\n"

    return out


# =========================================================
# CHECKLIST (SIMPLE STABLE)
# =========================================================
def checklist(text):
    if "intubation" not in text.lower():
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    return """
📋 CHECKLIST INTUBATION

☐ matériel
☐ aspiration
☐ capnographie
☐ médicaments
☐ plan B
☐ équipe prête
"""


# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = build_flow(user_input)

    elif mode == "QUICK ICU":
        answer = quick(user_input)

    elif mode == "PERFUSION ICU":
        drug, weight = detect_perf(user_input)
        answer = perfusion(drug, weight) if drug and weight else "💉 Données manquantes"

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
