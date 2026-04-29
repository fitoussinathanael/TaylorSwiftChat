import streamlit as st
import re
import sys

# =========================================================
# ❗ IMPORT RAG & SÉCURITÉ (BOILERPLATE ANTI-CRASH)
# =========================================================
try:
    from rag_icu import search_icu
except ImportError:
    def search_icu(query):
        return None

def safe_search_icu(query):
    """Garantit un retour string et empêche le crash sur None."""
    try:
        res = search_icu(query)
        return str(res or "").strip()
    except Exception:
        return ""

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.2", page_icon="🏥", layout="wide")
st.title("🏥 ICU ENGINE V10.2")
st.caption("ICU FLOW · Perfusion · Checklist · IA Clinique")

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
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU", "CHECKLIST PLATEAU", "IA CLINIQUE"]
)

# =========================================================
# SIDEBAR CONTEXTUELLE
# =========================================================
if mode == "ICU FLOW":
    st.sidebar.markdown("## 🧠 Patients")
    new_patient = st.sidebar.text_input("Créer patient")
    if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
        st.session_state.patients[new_patient] = {
            "cibles": {
                "hemodynamique": [], "respiratoire": [],
                "neuro": [], "renal": [], "infectieux": []
            },
            "numerics": {
                "pam": [], "norad": [], "fio2": [], "pf_ratio": [],
                "diurese": [], "creatinine": [], "lactate": [],
                "temperature": [], "spo2": []
            },
            "notes": []
        }
        st.session_state.current_patient = new_patient
        st.success(f"Patient créé : {new_patient}")

    patient_list = list(st.session_state.patients.keys())
    if patient_list:
        selected = st.sidebar.selectbox(
            "Patient actif", patient_list,
            index=patient_list.index(st.session_state.current_patient)
            if st.session_state.current_patient in patient_list else 0
        )
        st.session_state.current_patient = selected

elif mode == "PERFUSION ICU":
    st.sidebar.markdown("## 💉 Perfusion ICU")
    st.sidebar.info(
        "Tape : nom du médicament + poids patient\n\n"
        "Ex : `noradrénaline 70kg`"
    )

elif mode == "CHECKLIST PLATEAU":
    st.sidebar.markdown("## 📋 Checklist Plateau")
    st.sidebar.info("Ex : `intubation`, `voie centrale`")

elif mode == "IA CLINIQUE":
    st.sidebar.markdown("## 🧠 IA Clinique")
    st.sidebar.info("Ex : `critères sepsis-3`")

elif mode == "QUICK ICU":
    st.sidebar.markdown("## ⚡ Quick ICU")
    st.sidebar.info("Transmission rapide via RAG")

if st.sidebar.button("🔄 Reset session"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Entrée ICU...")

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC A — MOTEUR PERFUSION ICU
# ══════════════════════════════════════════════════════════
# =========================================================

CONCENTRATIONS = {
    "noradrénaline": {
        "concentration_mg_ml": 0.08,
        "unité": "µg/kg/min",
        "paliers": [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0],
        "fiche_rag": "noradrénaline"
    },
    "adrénaline": {
        "concentration_mg_ml": 0.04,
        "unité": "µg/kg/min",
        "paliers": [0.05, 0.1, 0.2, 0.3, 0.5],
        "fiche_rag": "adrénaline"
    },
    "dobutamine": {
        "concentration_mg_ml": 1.0,
        "unité": "µg/kg/min",
        "paliers": [2.5, 5, 7.5, 10, 15, 20],
        "fiche_rag": "dobutamine"
    },
    "propofol": {
        "concentration_mg_ml": 10.0,
        "unité": "mg/kg/h",
        "paliers":,
        "fiche_rag": "propofol"
    },
    "midazolam": {
        "concentration_mg_ml": 1.0,
        "unité": "mg/kg/h",
        "paliers": [0.03, 0.05, 0.1, 0.15, 0.2],
        "fiche_rag": "midazolam"
    },
    "kétamine": {
        "concentration_mg_ml": 2.0,
        "unité": "mg/kg/h",
        "paliers": [0.1, 0.2, 0.3, 0.5, 1.0, 1.5, 2.0],
        "fiche_rag": "kétamine"
    },
    "morphine": {
        "concentration_mg_ml": 1.0,
        "unité": "mg/kg/h",
        "paliers": [0.01, 0.02, 0.03, 0.05, 0.07, 0.1],
        "fiche_rag": "morphine"
    },
    "sufentanil": {
        "concentration_mg_ml": 0.005,
        "unité": "µg/kg/h",
        "paliers": [0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
        "fiche_rag": "sufentanil"
    },
    "vasopressine": {
        "concentration_mg_ml": 0.4,
        "unité": "U/h",
        "paliers": [0.01, 0.02, 0.03, 0.04],
        "fiche_rag": "vasopressine"
    },
    "furosémide": {
        "concentration_mg_ml": 2.0,
        "unité": "mg/h",
        "paliers":,
        "fiche_rag": "furosémide"
    },
    "héparine": {
        "concentration_mg_ml": 1.0,
        "unité": "U/kg/h",
        "paliers":,
        "fiche_rag": "héparine"
    },
    "insuline": {
        "concentration_mg_ml": 1.0,
        "unité": "U/h",
        "paliers":,
        "fiche_rag": "insuline"
    },
}

ALIASES = {
    "nora": "noradrénaline", "norad": "noradrénaline", "noradrénaline": "noradrénaline",
    "adré": "adrénaline", "dobu": "dobutamine", "propofol": "propofol", "midazolam": "midazolam",
    "kétamine": "kétamine", "morphine": "morphine", "sufentanil": "sufentanil",
    "vasopressine": "vasopressine", "furosémide": "furosémide", "héparine": "héparine", "insuline": "insuline",
}

def detect_drug_and_weight(text):
    t = text.lower()
    drug_found, weight_found = None, None
    for alias, canonical in ALIASES.items():
        if alias in t:
            drug_found = canonical
            break
    weight_match = re.findall(r'(\d{2,3})\s*kg', t)
    if weight_match: weight_found = int(weight_match[-1])
    return drug_found, weight_found

def calc_debit_ml_h(dose, weight, concentration_mg_ml, unite):
    if unite == "µg/kg/min": debit_exact = (dose * weight * 60) / (concentration_mg_ml * 1000)
    elif unite == "mg/kg/h": debit_exact = (dose * weight) / concentration_mg_ml
    elif unite == "µg/kg/h": debit_exact = (dose * weight) / (concentration_mg_ml * 1000)
    elif unite == "U/kg/h": debit_exact = (dose * weight) / concentration_mg_ml
    elif unite in ("mg/h", "U/h"): debit_exact = dose / concentration_mg_ml
    else: debit_exact = dose
    return debit_exact, round(debit_exact * 2) / 2

def format_perfusion_table(drug_name, weight, drug_data):
    conc, unite, paliers = drug_data["concentration_mg_ml"], drug_data["unité"], drug_data["paliers"]
    lines = [f"💉 **{drug_name.upper()}** — Poids : {weight} kg", f"Conc: {conc} mg/mL | Unité: {unite}", "", "| Dose | mL/h arrondi | mL/h exact |", "|------|-------------|------------|"]
    for dose in paliers:
        exact, arrondi = calc_debit_ml_h(dose, weight, conc, unite)
        lines.append(f"| {dose} {unite} | **{arrondi:.1f}** | ({exact:.2f}) |")
    return "\n".join(lines)

def format_perfusion_answer(drug_name, weight, drug_data, rag_context):
    table = format_perfusion_table(drug_name, weight, drug_data)
    rag_block = f"\n\n━━━━━━━━━━━━━━━━━━\n\n📖 FICHE {drug_name.upper()} (RAG)\n\n{rag_context}" if rag_context else ""
    return f"{table}{rag_block}\n\n👉 ICU ENGINE V10.2"

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC B — CHECKLIST PLATEAU
# ══════════════════════════════════════════════════════════
# =========================================================

CHECKLISTS = {
    "intubation": {
        "label": "Intubation oro-trachéale",
        "materiel": ["Laryngoscope", "Sonde IOT", "Capnographe", "Ambu", "Monitorage"],
        "medicaments": ["Hypnotique", "Curare", "Adrénaline prête"],
        "verification": ["Jeûne", "Allergies", "Aspiration testée"]
    },
    "voie centrale": {
        "label": "Pose voie veineuse centrale",
        "materiel": ["Kit VVC", "Champ stérile", "Échographe", "Fil à peau"],
        "medicaments": ["Lidocaïne 1%"],
        "verification": ["Hémostase", "Rx thorax post"]
    },
    "arrêt cardiaque": {
        "label": "Arrêt cardio-respiratoire",
        "materiel": ["Chariot d'urgence", "Défibrillateur", "Chronomètre RCP"],
        "medicaments": ["Adrénaline 1mg", "Amiodarone 300mg"],
        "verification": ["Heure début", "Leader désigné"]
    }
}

PROCEDURE_ALIASES = {"intubation": "intubation", "iot": "intubation", "voie centrale": "voie centrale", "vvc": "voie centrale", "acr": "arrêt cardiaque", "arrêt": "arrêt cardiaque"}

def detect_procedure(text):
    t = text.lower()
    for alias, canonical in PROCEDURE_ALIASES.items():
        if alias in t: return canonical
    return None

def format_checklist(proc_name, data):
    lines = [f"📋 **CHECKLIST — {data['label'].upper()}**", "", "🔧 **MATÉRIEL**"]
    for item in data["materiel"]: lines.append(f"  ☐ {item}")
    lines.append("\n💊 **MÉDICAMENTS**")
    for item in data["medicaments"]: lines.append(f"  ☐ {item}")
    lines.append("\n✅ **VÉRIFICATIONS**")
    for item in data["verification"]: lines.append(f"  ☐ {item}")
    return "\n".join(lines)

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC C — IA CLINIQUE
# ══════════════════════════════════════════════════════════
# =========================================================

def format_ia_clinique(question, rag_context):
    rag_block = rag_context if rag_context else "Aucun document trouvé."
    ia_lines = ["**Analyse IA**", "- Sepsis: Hémocultures, Lactate", "- SDRA: Vt 6mL/kg, Plateau < 30"]
    return f"📖 RÉPONSE RAG\n{rag_block}\n\n🧠 ENRICHISSEMENT IA\n" + "\n".join(ia_lines)

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC D — MOTEUR CLINIQUE ICU FLOW
# ══════════════════════════════════════════════════════════
# =========================================================

def extract_numerics(text):
    t = text.lower()
    found = {}
    pam = re.findall(r'pam[^\d]*(\d{2,3})', t)
    if pam: found["pam"] = int(pam[-1])
    norad = re.findall(r'norad[^\d]*(\d+[.,]\d+)', t)
    if norad: found["norad"] = float(norad[-1].replace(",", "."))
    lactate = re.findall(r'lactate[^\d]*(\d+[.,]\d+)', t)
    if lactate: found["lactate"] = float(lactate[-1].replace(",", "."))
    return found

def update_numerics(patient, new_vals):
    for k, v in new_vals.items():
        if k in patient["numerics"]:
            patient["numerics"][k].append(v)
            patient["numerics"][k] = patient["numerics"][k][-5:]

def analyze_numerics(patient):
    analysis = {}
    pam = patient["numerics"]["pam"][-1] if patient["numerics"]["pam"] else None
    if pam: analysis["pam"] = ("critique", f"PAM {pam}") if pam < 65 else ("ok", f"PAM {pam}")
    return analysis

def extract_clinical(text):
    t = text.lower()
    data = {"hemodynamique": [], "respiratoire": [], "neuro": [], "renal": [], "infectieux": []}
    if "norad" in t: data["hemodynamique"].append("noradrénaline")
    if "choc" in t: data["hemodynamique"].append("choc")
    return data

def compute_flags(text, cibles):
    return {"choc": "choc" in text.lower(), "sepsis": "sepsis" in text.lower()}

def build_icu_flow_answer(main, prio, critique, evolution, numeric_panel):
    return f"🎯 PROBLÈME\n{main}\n\n⚡ PRIORITÉ\n{prio}\n\n📊 MONITOR\n{critique}\n\n📈 ÉVOLUTION: {evolution}\n\n🔢 VALEURS\n{numeric_panel}"

# =========================================================
# DISPATCH PRINCIPAL
# =========================================================

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    if mode == "ICU FLOW":
        if not st.session_state.current_patient:
            st.warning("⚠️ Sélectionnez un patient"); st.stop()
        patient = st.session_state.patients[st.session_state.current_patient]
        extracted = extract_clinical(user_input)
        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]: patient["cibles"][k].append(item)
        new_num = extract_numerics(user_input)
        update_numerics(patient, new_num)
        analysis = analyze_numerics(patient)
        critique = analysis["pam"] if "pam" in analysis else "Stable"
        answer = build_icu_flow_answer("Instabilité", "Titrer Norad", critique, "Stable", "PAM détectée")

    elif mode == "QUICK ICU":
        context = safe_search_icu(user_input)
        answer = f"⚡ **QUICK ICU**\n\n{context or 'Aucun résultat.'}"

    elif mode == "PERFUSION ICU":
        drug_name, weight = detect_drug_and_weight(user_input)
        if not drug_name: answer = "Médicament non reconnu."
        elif not weight: answer = "Poids manquant."
        else:
            drug_data = CONCENTRATIONS[drug_name]
            rag_context = safe_search_icu(drug_data["fiche_rag"])
            answer = format_perfusion_answer(drug_name, weight, drug_data, rag_context)

    elif mode == "CHECKLIST PLATEAU":
        proc = detect_procedure(user_input)
        answer = format_checklist(proc, CHECKLISTS[proc]) if proc else "Procédure inconnue."

    elif mode == "IA CLINIQUE":
        rag_context = safe_search_icu(user_input)
        answer = format_ia_clinique(user_input, rag_context)

    else: answer = "Mode non reconnu."

    with st.chat_message("assistant"): st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
