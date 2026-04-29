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
# CHAT
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
# ICU FLOW
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

    if sofa >= 5:
        severity = "🔴 CRITIQUE"
    elif sofa >= 3:
        severity = "🟠 SÉVÈRE"
    else:
        severity = "🟡 MODÉRÉ"

    pam = compute_map(text)

    assessment = (
        "Hypoxémie + instabilité hémodynamique suspectées"
        if resp_score >= 2 and shock_score >= 2
        else "Évaluation en cours"
    )

    alerts = []
    if resp_score >= 2:
        alerts.append("🫁 ALERTE RESPIRATOIRE")
    if shock_score >= 2:
        alerts.append("🫀 ALERTE CHOC")
    if severity == "🔴 CRITIQUE":
        alerts.append("🚨 RISQUE RÉANIMATION / INTUBATION")

    return f"""
🧠 ICU FLOW STRUCTURÉ

🎯 CIBLES : {" | ".join(targets)}

📊 SCORE RESP : {resp_score} | SCORE CHOC : {shock_score} | SOFA-L : {sofa}
⚠️ GRAVITÉ : {severity}

{"🚨 ALERTES : " + " ".join(alerts) if alerts else ""}

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
# QUICK ICU
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
# PERFUSION
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "steps": [1, 2, 3, 4]},
    "midazolam": {"conc": 1, "unit": "mg/kg/h", "steps": [0.05, 0.1, 0.2]}
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
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
        return round(((dose * weight * 60) / (conc * 1000))*2)/2
    return round(((dose * weight) / conc)*2)/2

def perfusion(drug, weight):
    d = DRUGS[drug]

    out = f"💉 {drug.upper()} — {weight} kg\n\n"
    for dose in d["steps"]:
        out += f"{dose} → {calc(dose, weight, d['conc'], d['unit'])} mL/h\n"

    rag = safe_rag(drug)
    if rag:
        out += f"\n📖 {rag.get('classe','')} - {rag.get('usage','')}"

    return out

# =========================================================
# CHECKLIST (VERSION PRO UTILISABLE PLATEAU)
# =========================================================
def checklist(text):
    t = text.lower()

    if "intubation" not in t:
        return "📋 CHECKLIST\n❌ Spécifie : intubation"

    return """
📋 CHECKLIST INTUBATION (PLATEAU)

🔧 MATÉRIEL
☐ Laryngoscope + lame
☐ Sondes (7.0–8.0)
☐ Mandrin
☐ Seringue 10 mL
☐ Ambu + masque
☐ Capnographie
☐ Aspiration fonctionnelle
☐ Oxygène prêt
☐ Monitoring complet

💊 MÉDICAMENTS
☐ Hypnotique prêt (étomidate / kétamine / propofol)
☐ Curare prêt (suxaméthonium / rocuronium)
☐ Noradrénaline prête

✅ VÉRIFICATIONS
☐ Voie veineuse OK
☐ Monitoring actif
☐ Plan B (VMI / Fastrach / crico)
☐ Matériel testé

🚨 POINT CRITIQUE
☐ Intubation en séquence rapide prête
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
