import streamlit as st
import re

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V12", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V12")
st.caption("FLOW · QUICK ICU · PERFUSION · CHECKLIST (RÉA READY)")

# =========================================================
# SESSION
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

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
# CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# MAP
# =========================================================
def compute_map(text):
    m = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not m:
        return None
    sys = int(m.group(1))
    dia = int(m.group(2))
    return round((sys + 2 * dia) / 3, 1)

# =========================================================
# ICU FLOW
# =========================================================
def icu_flow(text):
    t = text.lower()

    resp = 2 if any(x in t for x in ["hypox", "dysp", "sat", "o2"]) else 0
    cardio = 2 if any(x in t for x in ["choc", "hypotension", "norad"]) else 0
    inf = 1 if any(x in t for x in ["fièvre", "infection", "pneumonie", "sepsis"]) else 0
    neuro = 2 if any(x in t for x in ["confus", "coma", "glasgow"]) else 0

    sofa = resp + cardio + inf + neuro

    if sofa >= 6:
        severity = "🔴 CRITIQUE"
    elif sofa >= 4:
        severity = "🟠 SÉVÈRE"
    else:
        severity = "🟡 MODÉRÉ"

    return f"""
🧠 ICU FLOW

📊 SOFA simplifié : {sofa}
⚠️ Gravité : {severity}

🫁 Resp : {resp} | 🫀 Cardio : {cardio} | 🦠 Inf : {inf} | 🧠 Neuro : {neuro}

🩺 PAM : {compute_map(text) or "N/A"}
"""

# =========================================================
# QUICK ICU (VERSION RÉA CORRIGÉE)
# =========================================================
def quick(text):
    t = text.lower()

    hypox = 2 if any(x in t for x in ["hypox", "dysp", "sat", "86%", "85%", "détresse respiratoire"]) else 0
    choc = 3 if any(x in t for x in ["choc", "hypotension", "85/50", "norad", "suspecté"]) else 0
    sepsis = 2 if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]) else 0
    neuro = 2 if any(x in t for x in ["confus", "coma", "glasgow"]) else 0

    score = hypox + choc + sepsis + neuro

    targets = []
    actions = []

    if hypox:
        targets.append("🫁 SpO2 > 92%")
        actions.append("O2 / VNI / intubation si échec")

    if choc:
        targets.append("🫀 PAM ≥ 65 mmHg")
        actions.append("Remplissage + noradrénaline")

    if sepsis:
        targets.append("🦠 ATB < 1h + contrôle source")
        actions.append("ATB probabiliste immédiate")

    if neuro:
        targets.append("🧠 Protection neurologique")
        actions.append("Scanner + protection VAS")

    if score >= 6:
        severity = "🔴 CRITIQUE"
    elif score >= 4:
        severity = "🟠 SÉVÈRE"
    else:
        severity = "🟡 MODÉRÉ"

    return f"""
⚡ QUICK ICU — RÉA

🎯 CIBLES :
{" | ".join(targets) if targets else "Non définies"}

⚠️ GRAVITÉ : {severity}
📊 SCORE : {score}

🧠 ACTIONS :
- {"\n- ".join(actions) if actions else "Surveillance"}

📝 INPUT :
{text}
"""

# =========================================================
# PERFUSION ICU (SAFE)
# =========================================================
DRUGS = {
    "noradrenaline": (0.08, [0.05, 0.1, 0.2, 0.5]),
    "propofol": (10, [1, 2, 3, 4])
}

ALIASES = {
    "norad": "noradrenaline",
    "nora": "noradrenaline",
    "propofol": "propofol"
}

def detect(text):
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

def perfusion(text):
    drug, weight = detect(text)

    if not drug or not weight:
        return "💉 Données manquantes (ex: noradrenaline 70 kg)"

    conc, steps = DRUGS[drug]

    out = f"💉 {drug.upper()} — {weight} kg\n\n"
    out += "DOSE | RÉEL\n"

    for d in steps:
        real = calc(d, weight, conc)
        out += f"{d} | {real}\n"

    return out

# =========================================================
# CHECKLIST DYNAMIQUE CORRIGÉE
# =========================================================
def checklist(text):
    t = text.lower()

    if "intubation" not in t:
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    hypox = any(x in t for x in ["hypox", "dysp", "sat", "84%", "85%", "détresse respiratoire"])
    choc = any(x in t for x in ["choc", "hypotension", "norad", "suspecté"])
    sepsis = any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"])

    out = """
📋 CHECKLIST INTUBATION (RÉA)

🔧 MATÉRIEL
☐ laryngoscope
☐ sonde adaptée
☐ capnographie
☐ aspiration
☐ O2 + BAVU
"""

    if hypox:
        out += """
🫁 HYPOXIE
☐ préoxygénation 3–5 min
☐ PEEP / VNI prêt
☐ anticipation désaturation
"""

    if choc:
        out += """
🫀 CHOC
☐ noradrénaline prête
☐ voie veineuse sécurisée
☐ monitoring TA continu
"""

    if sepsis:
        out += """
🦠 SEPSIS
☐ ATB immédiate
☐ lactates
"""

    out += """
🧠 STRATÉGIE
☐ plan A / B / C
☐ équipe prête
"""

    return out

# =========================================================
# DISPATCH
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "ICU FLOW":
        answer = icu_flow(user_input)

    elif mode == "QUICK ICU":
        answer = quick(user_input)

    elif mode == "PERFUSION ICU":
        answer = perfusion(user_input)

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
