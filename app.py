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
# PATIENT MANAGEMENT
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
        if isinstance(res, dict):
            return res
        return None
    except:
        return None

# =========================================================
# PERFUSION ICU
# =========================================================
DRUGS = {
    "noradrenaline": {"conc": 0.08, "unit": "µg/kg/min", "steps": [0.05, 0.1, 0.2, 0.5, 0.8, 1.0]},
    "propofol": {"conc": 10, "unit": "mg/kg/h", "steps": [1, 2, 3, 4, 5]},
    "midazolam": {"conc": 1, "unit": "mg/kg/h", "steps": [0.05, 0.1, 0.2, 0.3]}
}

ALIASES = {
    "nora": "noradrenaline",
    "norad": "noradrenaline",
    "noradrénaline": "noradrenaline",
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
        exact = (dose * weight * 60) / (conc * 1000)
    else:
        exact = (dose * weight) / conc

    ide = round(exact * 2) / 2
    return ide, exact


def perfusion(drug, weight):
    d = DRUGS[drug]

    out = f"💉 **{drug.upper()} — {weight} kg**\n\n"
    out += "| Dose | mL/h IDE | mL/h exact |\n"
    out += "|------|----------|-------------|\n"

    for dose in d["steps"]:
        ide, exact = calc(dose, weight, d["conc"], d["unit"])
        out += f"| {dose} | **{ide:.1f}** | ({exact:.2f}) |\n"

    rag = safe_rag(drug)

    if rag:
        out += "\n---\n📖 FICHE ICU\n\n"
        out += f"- Classe : {rag.get('classe','-')}\n"
        out += f"- Usage : {rag.get('usage','-')}\n"
        out += f"- Effets : {rag.get('effets','-')}\n"
        out += f"- Surveillance : {rag.get('surveillance','-')}\n"
        out += f"- Points ICU : {rag.get('points_icu','-')}\n"

    return out

# =========================================================
# CHECKLIST
# =========================================================
CHECKLIST = {
    "intubation": {
        "materiel": [
            "laryngoscope + lame",
            "sonde 7.0–8.0",
            "mandrin",
            "seringue 10 mL",
            "ambu + masque",
            "capnographie",
            "aspiration",
            "oxygène",
            "monitoring complet"
        ],
        "medicaments": [
            "hypnotique",
            "curare",
            "noradrénaline prête",
            "atropine si besoin"
        ],
        "verification": [
            "voie veineuse OK",
            "monitoring actif",
            "matériel testé",
            "plan B prêt"
        ]
    }
}

def checklist(text):
    if "intubation" not in text.lower():
        return "❌ Procédure non reconnue"

    d = CHECKLIST["intubation"]

    out = "📋 CHECKLIST INTUBATION\n\n"
    out += "🔧 MATÉRIEL\n" + "\n".join([f"☐ {x}" for x in d["materiel"]])
    out += "\n\n💊 MÉDICAMENTS\n" + "\n".join([f"☐ {x}" for x in d["medicaments"]])
    out += "\n\n✅ VÉRIFICATIONS\n" + "\n".join([f"☐ {x}" for x in d["verification"]])

    return out

# =========================================================
# 🔥 ICU FLOW + TRANSMISSION CLINIQUE (NOUVEAU)
# =========================================================
def flow(text):
    rag = safe_rag(text)

    # extraction simple cibles
    targets = []
    if "dyspnée" in text.lower() or "hypox" in text.lower():
        targets.append("🫁 Respiratoire")
    if "ta" in text.lower() or "hypotension" in text.lower():
        targets.append("🫀 Hémodynamique")
    if "sepsis" in text.lower():
        targets.append("🦠 Infectieux suspect")

    severity = "🟢 STABLE"
    if "85" in text or "hypox" in text.lower():
        severity = "🟠 MODÉRÉ À SÉVÈRE"
    if "choc" in text.lower() or "lactate" in text.lower():
        severity = "🔴 GRAVE / CHOC POSSIBLE"

    transmission = f"""
🧠 ICU FLOW STRUCTURÉ

🎯 CIBLES
{chr(10).join(targets) if targets else "⚠️ Non spécifiées"}

⚠️ GRAVITÉ : {severity}

📝 TRANSMISSION (SBAR SIMPLIFIÉ)

S - Situation :
{text}

B - Background :
Patient en contexte de réanimation / urgence vitale possible

A - Assessment :
- Terrain critique suspecté
- Surveillance rapprochée nécessaire

R - Recommendation :
- Monitorage continu
- Réévaluation clinique rapide
- Adaptation thérapeutique selon évolution
"""

    if rag:
        transmission += f"""

📖 RAG ICU
- {rag.get('classe','-')}
- {rag.get('usage','-')}
"""

    return transmission

# =========================================================
# QUICK ICU
# =========================================================
def quick(text):
    rag = safe_rag(text)

    if not rag:
        return "⚡ QUICK ICU\n\n❌ Aucun résultat RAG."

    return (
        "⚡ QUICK ICU\n\n"
        f"- Classe : {rag.get('classe','-')}\n"
        f"- Usage : {rag.get('usage','-')}\n"
        f"- Effets : {rag.get('effets','-')}\n"
        f"- Surveillance : {rag.get('surveillance','-')}\n"
        f"- Points ICU : {rag.get('points_icu','-')}\n"
    )

# =========================================================
# MAIN
# =========================================================
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    if mode == "PERFUSION ICU":
        drug, weight = detect_perf(user_input)
        if not drug:
            answer = "💉 Médicament non reconnu"
        elif not weight:
            answer = "⚠️ Poids manquant"
        else:
            answer = perfusion(drug, weight)

    elif mode == "CHECKLIST PLATEAU":
        answer = checklist(user_input)

    elif mode == "QUICK ICU":
        answer = quick(user_input)

    elif mode == "ICU FLOW":
        answer = flow(user_input)

    else:
        answer = "Mode inconnu"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
