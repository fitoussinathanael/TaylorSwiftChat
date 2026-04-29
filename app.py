import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.4 PRO", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.4 PRO")
st.caption("ICU FLOW · PERFUSION · CHECKLIST · QUICK ICU · RAG ICU")

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
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU"]
)

# =========================================================
# PATIENT
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
# CHAT HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# SAFE RAG
# =========================================================
def safe_rag(query: str):
    try:
        if not query:
            return None
        res = search_icu(query)
        return res if isinstance(res, dict) else None
    except:
        return None

# =========================================================
# PAM
# =========================================================
def compute_map(text):
    match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text)
    if not match:
        return None
    sys = int(match.group(1))
    dia = int(match.group(2))
    return round((sys + 2 * dia) / 3, 1)

# =========================================================
# ICU FLOW (inchangé)
# =========================================================
def build_flow(text):
    t = text.lower()

    targets = []
    if any(x in t for x in ["dysp", "hypox", "o2", "sat", "84%", "85%"]):
        targets.append("🫁 Respiratoire")
    if any(x in t for x in ["ta", "hypotension", "choc", "norad", "85/50"]):
        targets.append("🫀 Hémodynamique")
    if any(x in t for x in ["sepsis", "infection", "fièvre", "pneumonie"]):
        targets.append("🦠 Infectieux")

    resp_score = 0
    if "dysp" in t:
        resp_score += 1
    if "hypox" in t or "84%" in t or "85%" in t:
        resp_score += 2

    shock_score = 0
    if "ta" in t or "85/50" in t:
        shock_score += 2
    if "choc" in t:
        shock_score += 2
    if "norad" in t:
        shock_score += 2

    sofa = resp_score + shock_score

    severity = "🔴 CRITIQUE" if sofa >= 5 else "🟠 SÉVÈRE" if sofa >= 3 else "🟡 MODÉRÉ"

    pam = compute_map(text)

    assessment = (
        "Hypoxémie + instabilité hémodynamique suspectées"
        if resp_score >= 2 and shock_score >= 2
        else "Évaluation en cours"
    )

    return f"""
🧠 ICU FLOW STRUCTURÉ

🎯 CIBLES : {" | ".join(targets)}

📊 SCORE RESP : {resp_score} | SCORE CHOC : {shock_score} | SOFA-L : {sofa}
⚠️ GRAVITÉ : {severity}

🧠 ASSESSMENT :
{assessment}

🧾 TRANSMISSION (SBAR)

S - Situation :
{text}

B - Background :
Patient critique nécessitant surveillance rapprochée

A - Assessment :
{assessment}
🩺 PAM : {pam if pam else "N/A"} mmHg

R - Recommendation :
Monitorage continu
Réévaluation clinique rapide
Adaptation thérapeutique selon évolution
"""

# =========================================================
# QUICK ICU (inchangé)
# =========================================================
def quick(text):
    rag = safe_rag(text)
    if not rag:
        return "⚡ QUICK ICU\n\n❌ Aucun résultat RAG."

    return f"""
⚡ QUICK ICU

- Classe : {rag.get('classe','-')}
- Usage : {rag.get('usage','-')}
- Effets : {rag.get('effets','-')}
- Surveillance : {rag.get('surveillance','-')}
- ICU : {rag.get('points_icu','-')}
"""

# =========================================================
# PERFUSION ICU (AMÉLIORÉ TERRAIN)
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "steps": [1, 2, 3, 4]},
    "midazolam": {"conc": 1, "unit": "mg/kg/h", "steps": [0.05, 0.1, 0.2]}
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrenaline": "noradrenaline",
    "propofol": "propofol",
    "midazolam": "midazolam"
}

def detect_perf(text):
    t = text.lower()
    drug = None
    weight = None

    for a, v in ALIASES.items():
        if a in t:
            drug = v

    w = re.findall(r'(\d{2,3})\s*kg', t)
    if w:
        weight = int(w[0])

    return drug, weight

def calc(dose, weight, conc, unit):
    if unit == "µg/kg/min":
        return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2
    return round(((dose * weight) / conc) * 2) / 2

def perfusion(drug, weight):
    d = DRUGS[drug]

    out = f"""
💉 PERFUSION ICU

💊 {drug.upper()} — {weight} kg

*Exemple saisie : "noradrenaline 70 kg"*

────────────────────────────
📊 TABLEAU INFIRMIER
────────────────────────────
"""

    for dose in d["steps"]:
        calc_val = calc(dose, weight, d["conc"], d["unit"])
        out += f"""
- Dose : {dose} {d['unit']}
  → Débit : {calc_val} mL/h
"""

    rag = safe_rag(drug)
    if rag:
        out += f"""

📖 FICHE ICU :
- Classe : {rag.get('classe','')}
- Usage : {rag.get('usage','')}
"""

    return out

# =========================================================
# CHECKLIST (inchangé)
# =========================================================
def checklist(text):
    if "intubation" not in text.lower():
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    return """
📋 CHECKLIST INTUBATION

☐ Laryngoscope + lame
☐ Sondes 7.0–8.0
☐ Mandrin
☐ Seringue 10 mL
☐ Ambu
☐ Capnographie
☐ Aspiration
☐ O2 prêt
☐ Monitoring
☐ Hypnotique
☐ Curare
☐ Noradrénaline
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
        answer = perfusion(drug, weight) if drug and weight else "💉 Données manquantes (ex: noradrenaline 70 kg)"

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
