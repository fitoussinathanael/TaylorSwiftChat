import streamlit as st
import re
from rag_icu import search_icu

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
        "Ex : `noradrénaline 70kg`\n"
        "Ex : `midazolam 80kg`\n"
        "Ex : `propofol 65kg`"
    )

elif mode == "CHECKLIST PLATEAU":
    st.sidebar.markdown("## 📋 Checklist Plateau")
    st.sidebar.info(
        "Tape le nom de la procédure\n\n"
        "Ex : `intubation`\n"
        "Ex : `voie centrale`\n"
        "Ex : `drain thoracique`\n"
        "Ex : `arrêt cardiaque`"
    )

elif mode == "IA CLINIQUE":
    st.sidebar.markdown("## 🧠 IA Clinique")
    st.sidebar.info(
        "Question libre enrichie RAG + IA\n\n"
        "Ex : `critères sepsis-3`\n"
        "Ex : `protocole SDRA`\n"
        "Ex : `VAP bundle`"
    )

elif mode == "QUICK ICU":
    st.sidebar.markdown("## ⚡ Quick ICU")
    st.sidebar.info("Transmission rapide → synthèse via RAG")

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
#   Calcul doses + débits avec méthode arrondie (×12)
# ══════════════════════════════════════════════════════════
# =========================================================

# Dictionnaire concentrations standard réanimation
CONCENTRATIONS = {
    "noradrénaline": {
        "concentration_mg_ml": 0.08,  # 8mg/100mL standard
        "unité": "µg/kg/min",
        "paliers": [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0],
        "fiche_rag": "noradrénaline"
    },
    "adrénaline": {
        "concentration_mg_ml": 0.04,  # 4mg/100mL
        "unité": "µg/kg/min",
        "paliers": [0.05, 0.1, 0.2, 0.3, 0.5],
        "fiche_rag": "adrénaline"
    },
    "dobutamine": {
        "concentration_mg_ml": 1.0,   # 250mg/250mL
        "unité": "µg/kg/min",
        "paliers": [2.5, 5, 7.5, 10, 15, 20],
        "fiche_rag": "dobutamine"
    },
    "propofol": {
        "concentration_mg_ml": 10.0,  # 1% standard
        "unité": "mg/kg/h",
        "paliers": [1, 2, 3, 4, 5, 6],
        "fiche_rag": "propofol"
    },
    "midazolam": {
        "concentration_mg_ml": 1.0,   # 50mg/50mL
        "unité": "mg/kg/h",
        "paliers": [0.03, 0.05, 0.1, 0.15, 0.2],
        "fiche_rag": "midazolam"
    },
    "kétamine": {
        "concentration_mg_ml": 2.0,   # 200mg/100mL
        "unité": "mg/kg/h",
        "paliers": [0.1, 0.2, 0.3, 0.5, 1.0, 1.5, 2.0],
        "fiche_rag": "kétamine"
    },
    "morphine": {
        "concentration_mg_ml": 1.0,   # 50mg/50mL
        "unité": "mg/kg/h",
        "paliers": [0.01, 0.02, 0.03, 0.05, 0.07, 0.1],
        "fiche_rag": "morphine"
    },
    "sufentanil": {
        "concentration_mg_ml": 0.005, # 0.5µg/mL standard
        "unité": "µg/kg/h",
        "paliers": [0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
        "fiche_rag": "sufentanil"
    },
    "noradrénaline": {
        "concentration_mg_ml": 0.08,
        "unité": "µg/kg/min",
        "paliers": [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0],
        "fiche_rag": "noradrénaline"
    },
    "vasopressine": {
        "concentration_mg_ml": 0.4,   # 20U/50mL
        "unité": "U/h",
        "paliers": [0.01, 0.02, 0.03, 0.04],
        "fiche_rag": "vasopressine"
    },
    "furosémide": {
        "concentration_mg_ml": 2.0,   # 100mg/50mL
        "unité": "mg/h",
        "paliers": [2, 5, 10, 15, 20],
        "fiche_rag": "furosémide"
    },
    "héparine": {
        "concentration_mg_ml": 1.0,   # 25000U/50mL → ~500U/mL
        "unité": "U/kg/h",
        "paliers": [10, 15, 18, 20, 25],
        "fiche_rag": "héparine"
    },
    "insuline": {
        "concentration_mg_ml": 1.0,   # 50U/50mL = 1U/mL
        "unité": "U/h",
        "paliers": [1, 2, 3, 4, 5, 6, 8, 10],
        "fiche_rag": "insuline"
    },
}

# Alias pour la détection
ALIASES = {
    "nora": "noradrénaline",
    "norad": "noradrénaline",
    "noradrénaline": "noradrénaline",
    "noradrenaline": "noradrénaline",
    "adré": "adrénaline",
    "adrenaline": "adrénaline",
    "adrénaline": "adrénaline",
    "dobu": "dobutamine",
    "dobutamine": "dobutamine",
    "propofol": "propofol",
    "propo": "propofol",
    "midazolam": "midazolam",
    "midaz": "midazolam",
    "hypnovel": "midazolam",
    "kétamine": "kétamine",
    "ketamine": "kétamine",
    "keta": "kétamine",
    "morphine": "morphine",
    "sufentanil": "sufentanil",
    "sufen": "sufentanil",
    "vasopressine": "vasopressine",
    "furosémide": "furosémide",
    "furosemide": "furosémide",
    "lasilix": "furosémide",
    "héparine": "héparine",
    "heparine": "héparine",
    "insuline": "insuline",
}

def detect_drug_and_weight(text):
    """Détecte le médicament et le poids dans la saisie."""
    t = text.lower()
    drug_found = None
    weight_found = None

    for alias, canonical in ALIASES.items():
        if alias in t:
            drug_found = canonical
            break

    weight_match = re.findall(r'(\d{2,3})\s*kg', t)
    if weight_match:
        weight_found = int(weight_match[-1])
    else:
        weight_match2 = re.findall(r'(?:poids|kg)[^\d]*(\d{2,3})', t)
        if weight_match2:
            weight_found = int(weight_match2[-1])

    return drug_found, weight_found

def calc_debit_ml_h(dose, weight, concentration_mg_ml, unite):
    """
    Calcule le débit en mL/h selon l'unité.
    Retourne (débit_exact, débit_arrondi_méthode_×12)
    """
    if unite == "µg/kg/min":
        # dose µg/kg/min → mg/h
        debit_exact = (dose * weight * 60) / (concentration_mg_ml * 1000)
    elif unite == "mg/kg/h":
        debit_exact = (dose * weight) / concentration_mg_ml
    elif unite == "µg/kg/h":
        debit_exact = (dose * weight) / (concentration_mg_ml * 1000)
    elif unite == "U/kg/h":
        debit_exact = (dose * weight) / concentration_mg_ml
    elif unite in ("mg/h", "U/h"):
        debit_exact = dose / concentration_mg_ml
    else:
        debit_exact = dose

    # Méthode ×12 : arrondi au multiple de 0.5 le plus proche
    # utilisé en pratique infirmière réanimation
    arrondi = round(debit_exact * 2) / 2

    return debit_exact, arrondi

def format_perfusion_table(drug_name, weight, drug_data):
    """
    Génère le tableau de perfusion complet avec méthode arrondie + valeur exacte.
    """
    conc    = drug_data["concentration_mg_ml"]
    unite   = drug_data["unité"]
    paliers = drug_data["paliers"]

    lines = []
    lines.append(f"💉 **{drug_name.upper()}** — Poids : {weight} kg")
    lines.append(f"Concentration : {conc} mg/mL | Unité : {unite}")
    lines.append("")
    lines.append("| Dose | mL/h arrondi | mL/h exact |")
    lines.append("|------|-------------|------------|")

    for dose in paliers:
        exact, arrondi = calc_debit_ml_h(dose, weight, conc, unite)
        lines.append(f"| {dose} {unite} | **{arrondi:.1f}** | ({exact:.2f}) |")

    lines.append("")
    lines.append(f"📌 Méthode ×12 : arrondi au 0.5 mL/h le plus proche")
    lines.append(f"🔢 Concentration seringue standard service")

    return "\n".join(lines)

def format_perfusion_answer(drug_name, weight, drug_data, rag_context):
    """Sortie finale : tableau de calcul + fiche RAG."""
    table = format_perfusion_table(drug_name, weight, drug_data)

    rag_block = ""
    if rag_context and rag_context.strip():
        rag_block = f"\n\n━━━━━━━━━━━━━━━━━━\n\n📖 FICHE {drug_name.upper()} (RAG)\n\n{rag_context}"

    return f"{table}{rag_block}\n\n👉 ICU ENGINE V10.2 — PERFUSION ICU"

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC B — CHECKLIST PLATEAU
# ══════════════════════════════════════════════════════════
# =========================================================

CHECKLISTS = {
    "intubation": {
        "label": "Intubation oro-trachéale",
        "materiel": [
            "Laryngoscope + lames (Mac 3 / Mac 4)",
            "Sonde IOT (7.0 / 7.5 / 8.0) + mandrin",
            "Seringue 10 mL (gonflage ballonnet)",
            "Fixation sonde (Clinifix ou équivalent)",
            "Capnographe / EtCO2",
            "Aspirateur + sondes d'aspiration",
            "Ambu + masque facial",
            "Oxygène branché + débit",
            "Voie veineuse périphérique fonctionnelle",
            "Monitorage : SpO2 / FC / PA / ECG",
        ],
        "medicaments": [
            "Hypnotique : étomidate 0.3 mg/kg ou kétamine 1-2 mg/kg",
            "Curare : succinylcholine 1 mg/kg ou rocuronium 1.2 mg/kg",
            "Atropine 0.5 mg (si bradycardie anticipée)",
            "Adrénaline 1 mg prête (urgence)",
        ],
        "verification": [
            "Jeûne vérifié (si électif)",
            "Allergie vérifiée",
            "Matelas de déglutition en place",
            "Aspiration testée + fonctionnelle",
        ]
    },
    "voie centrale": {
        "label": "Pose voie veineuse centrale",
        "materiel": [
            "Kit VVC (cathéter + guide + dilatateur)",
            "Champ stérile grand format",
            "Compresses stériles + cupules",
            "Bétadine / chlorhexidine alcoolique",
            "Seringues 10 mL × 4 + aiguille",
            "NaCl 0.9% pour rinçage",
            "Fil à peau + porte-aiguille + ciseau",
            "Pansement occlusif transparent",
            "Échographe + sonde vasculaire + gel stérile",
            "Monitorage continu",
        ],
        "medicaments": [
            "Lidocaïne 1% pour anesthésie locale",
            "Héparine 5U/mL pour rinçage (selon protocole)",
        ],
        "verification": [
            "Consentement / information patient",
            "Hémostase vérifiée",
            "Position Trendelenburg disponible",
            "Rx thorax post-geste prévu",
        ]
    },
    "drain thoracique": {
        "label": "Drainage thoracique",
        "materiel": [
            "Kit drain thoracique (20-28 Fr selon indication)",
            "Bistouri lame 15 + pince Kelly",
            "Champ stérile + gants stériles",
            "Compresses + bétadine / chlorhexidine",
            "Fil à peau non résorbable",
            "Système de drainage (Pleur-Evac ou équivalent)",
            "Raccord + tubulure",
            "Pansement occlusif + sparadrap",
            "Aspirateur si drainage actif",
        ],
        "medicaments": [
            "Lidocaïne 1% anesthésie locale (max 3 mg/kg)",
            "Morphine IV titrée si douleur majeure",
            "Midazolam 1-2 mg si anxiété importante",
        ],
        "verification": [
            "Rx thorax pré-geste disponible",
            "Côté à drainer confirmé ×2",
            "Hémostase vérifiée",
            "Rx thorax post-geste prévu",
        ]
    },
    "arrêt cardiaque": {
        "label": "Arrêt cardio-respiratoire",
        "materiel": [
            "Chariot d'urgence vérifié",
            "Défibrillateur allumé + électrodes en place",
            "Ambu + masque + O2 haut débit",
            "Matériel intubation prêt (cf. checklist IOT)",
            "Voie veineuse × 2 ou IO si impossible",
            "Monitorage ECG continu",
            "Chronomètre RCP",
        ],
        "medicaments": [
            "Adrénaline 1 mg/10 mL × 5 ampoules prêtes",
            "Amiodarone 300 mg IV (FV réfractaire)",
            "Atropine 1 mg (si asystolie / BAV)",
            "NaCl 0.9% 500 mL × 2 (remplissage)",
            "Bicarbonate 8.4% (si ACR > 15 min)",
        ],
        "verification": [
            "Heure de début ACR notée",
            "Leader désigné",
            "Rôles équipe répartis",
            "Famille prise en charge",
        ]
    },
    "ponction lombaire": {
        "label": "Ponction lombaire",
        "materiel": [
            "Kit PL stérile (aiguille 22G ou 25G)",
            "Champ troué stérile",
            "Compresses + bétadine / chlorhexidine",
            "Tubes numérotés × 4",
            "Manomètre (si mesure pression)",
            "Pansement post-geste",
        ],
        "medicaments": [
            "Lidocaïne 1% anesthésie locale",
            "EMLA 1h avant si patient non coopérant",
        ],
        "verification": [
            "Bilan hémostase disponible",
            "Fond d'œil / scanner si HTIC suspectée",
            "Allergie iode vérifiée",
            "Position fœtale ou assise confirmée",
        ]
    },
    "fibroscopie bronchique": {
        "label": "Fibroscopie bronchique",
        "materiel": [
            "Fibroscope + source lumière",
            "Gaine stérile + gel lubrifiant",
            "Sonde d'aspiration adaptée",
            "NaCl 0.9% sérum physiologique (LBA)",
            "Pots de prélèvement stériles étiquetés",
            "Aspiration fonctionnelle",
            "O2 supplémentaire disponible",
        ],
        "medicaments": [
            "Lidocaïne 1% nébulisation ou instillation",
            "Midazolam 1-2 mg si agitation (ventilé)",
            "Augmentation FiO2 pré-geste",
        ],
        "verification": [
            "Consentement / information",
            "SpO2 cible définie avant geste",
            "Ventilation adaptée si intubé",
            "Hémostase vérifiée si LBA",
        ]
    },
}

# Alias procédures
PROCEDURE_ALIASES = {
    "intubation": "intubation",
    "iot": "intubation",
    "isr": "intubation",
    "intubé": "intubation",
    "voie centrale": "voie centrale",
    "vvc": "voie centrale",
    "central": "voie centrale",
    "cathéter central": "voie centrale",
    "drain": "drain thoracique",
    "drain thoracique": "drain thoracique",
    "drainage": "drain thoracique",
    "pneumothorax": "drain thoracique",
    "arrêt cardiaque": "arrêt cardiaque",
    "acr": "arrêt cardiaque",
    "réanimation cardiaque": "arrêt cardiaque",
    "rcp": "arrêt cardiaque",
    "ponction lombaire": "ponction lombaire",
    "pl": "ponction lombaire",
    "fibroscopie": "fibroscopie bronchique",
    "fibro": "fibroscopie bronchique",
    "lba": "fibroscopie bronchique",
    "bronchoscopie": "fibroscopie bronchique",
}

def detect_procedure(text):
    t = text.lower()
    for alias, canonical in PROCEDURE_ALIASES.items():
        if alias in t:
            return canonical
    return None

def format_checklist(proc_name, data):
    """Formate la checklist plateau pour affichage."""
    lines = []
    lines.append(f"📋 **CHECKLIST — {data['label'].upper()}**")
    lines.append("")

    lines.append("🔧 **MATÉRIEL**")
    for item in data["materiel"]:
        lines.append(f"  ☐ {item}")
    lines.append("")

    lines.append("💊 **MÉDICAMENTS**")
    for item in data["medicaments"]:
        lines.append(f"  ☐ {item}")
    lines.append("")

    lines.append("✅ **VÉRIFICATIONS**")
    for item in data["verification"]:
        lines.append(f"  ☐ {item}")

    lines.append("")
    lines.append("👉 ICU ENGINE V10.2 — CHECKLIST PLATEAU")

    return "\n".join(lines)

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC C — IA CLINIQUE (RAG + enrichissement IA)
# ══════════════════════════════════════════════════════════
# =========================================================

def format_ia_clinique(question, rag_context):
    """
    2 blocs séparés : RAG brut + enrichissement IA.
    """
    # Bloc RAG
    rag_block = rag_context.strip() if rag_context and rag_context.strip() else "Aucun document trouvé dans la base."

    # Bloc IA enrichi : analyse contextuelle selon le contenu
    ia_lines = []
    q = question.lower()

    if any(x in q for x in ["sepsis", "choc septique", "sepsis-3"]):
        ia_lines = [
            "**Critères Sepsis-3 (2016)**",
            "- Infection suspectée ou confirmée",
            "- SOFA score ≥ 2 (ou qSOFA ≥ 2 en pré-hospit)",
            "- Choc septique : vasopresseur + lactate > 2 mmol/L malgré remplissage",
            "",
            "**Points clés terrain**",
            "- Lactate dans l'heure",
            "- Hémocultures avant antibio",
            "- Antibio dans l'heure si choc",
            "- Remplissage 30 mL/kg si hypovolémie",
        ]
    elif any(x in q for x in ["sdra", "ards", "ventilation protectrice"]):
        ia_lines = [
            "**SDRA — Critères Berlin**",
            "- Début < 7 jours d'un facteur déclenchant",
            "- Opacités bilatérales (non expliquées par épanchement)",
            "- P/F < 300 sous PEEP ≥ 5 cmH2O",
            "  → Léger : P/F 200-300 | Modéré : 100-200 | Sévère : < 100",
            "",
            "**Ventilation protectrice**",
            "- Vt 6 mL/kg (poids idéal)",
            "- Pression plateau < 30 cmH2O",
            "- PEEP selon table ARDSnet",
            "- Décubitus ventral si P/F < 150 (≥ 16h)",
        ]
    elif any(x in q for x in ["vap", "pneumopathie", "bundle", "prévention"]):
        ia_lines = [
            "**VAP Bundle — Prévention pneumopathie sous VM**",
            "- Surélévation tête de lit 30-45°",
            "- Hygiène bucco-dentaire × 3/j (chlorhexidine)",
            "- Dépressurisation ballonnet ≤ 20 cmH2O / réévaluation",
            "- Pause sédation quotidienne (SAT)",
            "- Évaluation quotidienne sevrage ventilatoire (SBT)",
            "- Voie centrale ombilicale : évaluation J1",
        ]
    elif any(x in q for x in ["rass", "sédation", "analgésie", "cam-icu"]):
        ia_lines = [
            "**Score RASS — Objectifs réanimation**",
            "- RASS 0 : éveillé, calme (cible standard)",
            "- RASS -1 à -2 : sédation légère (cible agitation)",
            "- RASS -3 à -5 : sédation profonde (HTIC, SDRA sévère)",
            "",
            "**Analgésie-Sédation-Délire (ASD)**",
            "- Analgésie d'abord (analgésie-based sedation)",
            "- CAM-ICU si RASS ≥ -3 (dépistage délire)",
            "- Dexmedetomidine si agitation sans douleur",
        ]
    elif any(x in q for x in ["irc", "ira", "épuration", "hémodialyse", "irrt"]):
        ia_lines = [
            "**IRA en réanimation — Critères KDIGO**",
            "- Stade 1 : créat ×1.5 ou diurèse < 0.5 mL/kg/h × 6h",
            "- Stade 2 : créat ×2 ou diurèse < 0.5 mL/kg/h × 12h",
            "- Stade 3 : créat ×3 ou diurèse < 0.3 mL/kg/h × 24h",
            "",
            "**Indications EER urgentes**",
            "- Oligurie réfractaire / anurie",
            "- Hyperkaliémie > 6.5 mmol/L",
            "- Acidose métabolique pH < 7.15",
            "- Surcharge hydrique réfractaire",
        ]
    else:
        ia_lines = [
            "**Analyse IA**",
            f"Question : {question}",
            "",
            "Pas de règle spécifique détectée.",
            "Résultat RAG disponible ci-dessus.",
            "Précise la question pour une réponse enrichie.",
        ]

    ia_block = "\n".join(ia_lines)

    return f"""
📖 RÉPONSE RAG
━━━━━━━━━━━━━━━━━━
{rag_block}

━━━━━━━━━━━━━━━━━━

🧠 ENRICHISSEMENT IA
━━━━━━━━━━━━━━━━━━
{ia_block}

👉 ICU ENGINE V10.2 — IA CLINIQUE
"""

# =========================================================
# ══════════════════════════════════════════════════════════
#   BLOC D — MOTEUR CLINIQUE ICU FLOW
# ══════════════════════════════════════════════════════════
# =========================================================

def extract_numerics(text):
    t = text.lower()
    found = {}

    pam = re.findall(r'(?:map|pam)[^\d]*(\d{2,3})', t)
    if pam:
        found["pam"] = int(pam[-1])
    pam_range = re.findall(r'entre\s+(\d{2,3})\s+et\s+(\d{2,3})\s*(?:mmhg)?', t)
    if pam_range and "pam" not in found:
        found["pam"] = int(pam_range[-1][0])

    norad = re.findall(r'(?:norad|nora|noradrénaline)[^\d]*(\d+[.,]\d+)', t)
    if norad:
        found["norad"] = float(norad[-1].replace(",", "."))

    fio2 = re.findall(r'fio2\s*[:\-]?\s*(\d{2,3})\s*%?', t)
    if fio2:
        found["fio2"] = int(fio2[-1])

    spo2 = re.findall(r'spo2\s*[:\-]?\s*(\d{2,3})\s*%?', t)
    if spo2:
        found["spo2"] = int(spo2[-1])

    pf = re.findall(r'(?:p/f|pf|rapport\s*p/?f)[^\d]*(\d{2,3})', t)
    if pf:
        found["pf_ratio"] = int(pf[-1])

    diurese = re.findall(r'(?:diur[eèé]se)[^\d]*(\d+[.,]?\d*)\s*(?:ml/kg|ml)', t)
    if diurese:
        found["diurese"] = float(diurese[-1].replace(",", "."))
    diurese2 = re.findall(r'(\d+[.,]\d+)\s*ml/kg/h', t)
    if diurese2 and "diurese" not in found:
        found["diurese"] = float(diurese2[-1].replace(",", "."))

    creat = re.findall(r'cr[eé]atinine[^\d]*(\d{2,4})', t)
    if creat:
        found["creatinine"] = int(creat[-1])

    lactate = re.findall(r'lactat[e]?[^\d]*(\d+[.,]\d+)', t)
    if lactate:
        found["lactate"] = float(lactate[-1].replace(",", "."))

    temp = re.findall(r'(?:fièvre|température|temp)[^\d]*(\d{2}[.,]\d)', t)
    if temp:
        found["temperature"] = float(temp[-1].replace(",", "."))
    temp2 = re.findall(r'(\d{2}[.,]\d)\s*°c', t)
    if temp2 and "temperature" not in found:
        found["temperature"] = float(temp2[-1].replace(",", "."))

    return found

def update_numerics(patient, new_vals):
    for k, v in new_vals.items():
        if k in patient["numerics"]:
            patient["numerics"][k].append(v)
            patient["numerics"][k] = patient["numerics"][k][-5:]

def get_last(patient, key):
    vals = patient["numerics"].get(key, [])
    return vals[-1] if vals else None

def analyze_numerics(patient):
    analysis = {}

    pam = get_last(patient, "pam")
    if pam is not None:
        if pam < 60:
            analysis["pam"] = ("critique", f"PAM {pam} mmHg")
        elif pam < 65:
            analysis["pam"] = ("limite", f"PAM {pam} mmHg")
        else:
            analysis["pam"] = ("ok", f"PAM {pam} mmHg")

    norad = get_last(patient, "norad")
    if norad is not None:
        if norad >= 0.5:
            analysis["norad"] = ("critique", f"Norad {norad} µg/kg/min")
        elif norad >= 0.25:
            analysis["norad"] = ("limite", f"Norad {norad} µg/kg/min")
        else:
            analysis["norad"] = ("ok", f"Norad {norad} µg/kg/min")

    pf = get_last(patient, "pf_ratio")
    fio2 = get_last(patient, "fio2")
    if pf is not None:
        if pf < 100:
            analysis["respiratoire"] = ("critique", f"P/F {pf}")
        elif pf < 200:
            analysis["respiratoire"] = ("limite", f"P/F {pf}")
        elif pf < 300:
            analysis["respiratoire"] = ("surveillance", f"P/F {pf}")
        else:
            analysis["respiratoire"] = ("ok", f"P/F {pf}")
    elif fio2 is not None:
        if fio2 >= 80:
            analysis["respiratoire"] = ("critique", f"FiO2 {fio2}%")
        elif fio2 >= 60:
            analysis["respiratoire"] = ("limite", f"FiO2 {fio2}%")
        else:
            analysis["respiratoire"] = ("ok", f"FiO2 {fio2}%")

    diurese = get_last(patient, "diurese")
    if diurese is not None:
        if diurese < 0.3:
            analysis["diurese"] = ("critique", f"Diurèse {diurese} mL/kg/h")
        elif diurese < 0.5:
            analysis["diurese"] = ("limite", f"Diurèse {diurese} mL/kg/h")
        else:
            analysis["diurese"] = ("ok", f"Diurèse {diurese} mL/kg/h")

    creat = get_last(patient, "creatinine")
    if creat is not None:
        if creat > 300:
            analysis["creatinine"] = ("critique", f"Créatinine {creat} µmol/L")
        elif creat > 150:
            analysis["creatinine"] = ("limite", f"Créatinine {creat} µmol/L")
        else:
            analysis["creatinine"] = ("ok", f"Créatinine {creat} µmol/L")

    lactate = get_last(patient, "lactate")
    if lactate is not None:
        if lactate >= 4:
            analysis["lactate"] = ("critique", f"Lactate {lactate} mmol/L")
        elif lactate >= 2:
            analysis["lactate"] = ("limite", f"Lactate {lactate} mmol/L")
        else:
            analysis["lactate"] = ("ok", f"Lactate {lactate} mmol/L")

    temp = get_last(patient, "temperature")
    if temp is not None:
        if temp >= 39.5:
            analysis["temperature"] = ("critique", f"T° {temp}°C")
        elif temp >= 38.5:
            analysis["temperature"] = ("limite", f"T° {temp}°C")
        else:
            analysis["temperature"] = ("ok", f"T° {temp}°C")

    return analysis

def extract_clinical(text):
    t = text.lower()
    data = {
        "hemodynamique": [], "respiratoire": [],
        "neuro": [], "renal": [], "infectieux": []
    }

    if "norad" in t or "nora" in t or "vasopresseur" in t:
        data["hemodynamique"].append("noradrénaline")
    if "hypotension" in t or "map" in t or "instabilité" in t or "pam" in t:
        data["hemodynamique"].append("instabilité tensionnelle")
    if "choc" in t:
        data["hemodynamique"].append("choc")

    if "ventil" in t or "intub" in t or "peep" in t or "fio2" in t:
        data["respiratoire"].append("ventilation mécanique")
    if "hypoxém" in t or "spo2" in t or "crépitant" in t:
        data["respiratoire"].append("hypoxémie")

    if "propof" in t:
        data["neuro"].append("propofol")
    if "midaz" in t:
        data["neuro"].append("midazolam")
    if "agitation" in t:
        data["neuro"].append("agitation")
    if "sédation" in t or "sedation" in t:
        data["neuro"].append("sédation")

    if "creat" in t or "diurese" in t or "oligurie" in t or "diurèse" in t:
        data["renal"].append("insuffisance rénale")

    if "sepsis" in t or "choc septique" in t:
        data["infectieux"].append("sepsis")
    if "infection" in t or "infectieux" in t or "antibio" in t:
        data["infectieux"].append("infection active")
    if "fièvre" in t or "38" in t or "39" in t or "hémoculture" in t:
        data["infectieux"].append("foyer infectieux")

    return data

def compute_flags(text, cibles):
    t = text.lower()
    all_data = " ".join(" ".join(v) for v in cibles.values()).lower()
    return {
        "vasopresseur": "noradrénaline" in all_data or "norad" in t or "vasopresseur" in t,
        "hypotension":  "instabilité tensionnelle" in all_data or "hypotension" in t or "map" in t or "pam" in t,
        "choc":         "choc" in all_data or "choc" in t,
        "sepsis":       "sepsis" in all_data or "sepsis" in t,
        "infection":    "infection" in all_data or "antibio" in t or "hémoculture" in t,
        "ventilation":  "ventilation mécanique" in all_data or "ventil" in t or "intub" in t,
        "hypoxemie":    "hypoxémie" in all_data or "hypoxém" in t or "fio2" in t or "crépitant" in t,
        "sedation":     any(x in all_data for x in ["propofol", "midazolam", "sédation"]),
        "renal":        "insuffisance rénale" in all_data or "creat" in t or "oligurie" in t or "diurèse" in t,
        "agitation":    "agitation" in all_data,
        "aggravation":  any(x in t for x in [
            "aggrav", "progression", "dégradation", "fluctuante",
            "persistante", "sévère", "positives"
        ])
    }

def detect_pam_risk(text, flags, num_analysis):
    if "pam" in num_analysis:
        level, _ = num_analysis["pam"]
        return {"critique": "basse", "limite": "limite"}.get(level, "correcte")
    t = text.lower()
    if any([flags["choc"] and flags["vasopresseur"],
            flags["vasopresseur"] and flags["hypotension"],
            "hypotension sévère" in t]):
        return "basse"
    if any([flags["vasopresseur"] and not flags["hypotension"],
            flags["hypotension"] and not flags["vasopresseur"],
            "fluctuante" in t]):
        return "limite"
    if flags["vasopresseur"] or flags["hypotension"] or flags["choc"]:
        return "limite"
    return None

def build_main_problem(flags, pam_level, num_analysis):
    norad = num_analysis.get("norad")
    norad_str = f" sous norad {norad[1].split()[1]} µg/kg/min" if norad else ""

    if flags["choc"] and flags["sepsis"] and flags["vasopresseur"]:
        pam = num_analysis.get("pam")
        pam_str = f" — {pam[1]}" if pam else ""
        return f"Choc septique vasoplégique{norad_str}{pam_str}"
    if flags["sepsis"] and flags["vasopresseur"]:
        return f"Sepsis sévère avec dépendance vasopressive{norad_str}"
    resp = num_analysis.get("respiratoire")
    if flags["hypoxemie"] and flags["ventilation"] and not flags["vasopresseur"]:
        resp_str = f" — {resp[1]}" if resp else ""
        return f"Défaillance respiratoire sous ventilation invasive{resp_str}"
    if flags["vasopresseur"] and flags["hypotension"]:
        return f"Instabilité hémodynamique sous vasopresseurs{norad_str}"
    organ_count = sum([
        flags["vasopresseur"],
        flags["hypoxemie"] or flags["ventilation"],
        flags["renal"]
    ])
    if organ_count >= 2:
        return "Défaillance multi-organe en cours — surveillance rapprochée"
    return "Patient instable — évaluation multi-systémique requise"

def build_action_prioritaire(flags, pam_level, num_analysis):
    pam = num_analysis.get("pam")
    if flags["choc"] and flags["sepsis"]:
        if pam_level in ("basse", "limite"):
            pam_str = f"({pam[1]} → cible ≥ 65)" if pam else "(cible ≥ 65 mmHg)"
            return f"Titrer noradrénaline {pam_str} + antibiothérapie si non débutée"
        return "Antibiothérapie probabiliste immédiate + contrôle hémodynamique"
    if pam_level == "basse":
        pam_str = f"({pam[1]})" if pam else ""
        return f"Titration vasopresseur urgente {pam_str} — objectif PAM ≥ 65 mmHg"
    if flags["hypoxemie"] and flags["ventilation"]:
        resp = num_analysis.get("respiratoire")
        resp_str = f"({resp[1]})" if resp else ""
        return f"Optimisation ventilatoire {resp_str} — adapter FiO2 / PEEP"
    if flags["sepsis"] and flags["infection"]:
        return "Hémocultures + antibiothérapie probabiliste dans l'heure"
    if pam_level == "limite":
        return "Surveillance MAP continue — titrer si < 65 mmHg"
    if flags["renal"]:
        return "Surveillance diurèse horaire stricte + bilan rénal"
    return "Réévaluation clinique complète — paramètres à stabiliser"

def build_monitor_alerts_fused(flags, pam_level, num_analysis):
    critique  = []
    important = []
    surveillance = []

    pam     = num_analysis.get("pam")
    norad   = num_analysis.get("norad")
    resp    = num_analysis.get("respiratoire")
    diurese = num_analysis.get("diurese")
    creat   = num_analysis.get("creatinine")
    lactate = num_analysis.get("lactate")
    temp    = num_analysis.get("temperature")

    # Cluster hémodynamique
    if flags["vasopresseur"] or flags["choc"] or pam_level in ("basse", "limite"):
        parts = []
        if flags["choc"] and flags["sepsis"]:
            parts.append("choc septique")
        elif flags["vasopresseur"]:
            parts.append("vasopresseurs actifs")
        if norad:
            parts.append(norad[1])
        if pam:
            parts.append(pam[1])
        elif pam_level == "basse":
            parts.append("PAM < 65 mmHg")
        elif pam_level == "limite":
            parts.append("PAM limite")
        label = " / ".join(parts) if parts else "instabilité hémodynamique"
        if pam_level == "basse" or (flags["choc"] and flags["sepsis"]):
            critique.append(f"🫀 {label}")
        else:
            important.append(f"🫀 {label}")

    # Cluster respiratoire
    if flags["ventilation"] or flags["hypoxemie"]:
        parts = []
        if flags["ventilation"]:
            parts.append("VM invasive")
        if flags["hypoxemie"]:
            parts.append("hypoxémie")
        if resp:
            parts.append(resp[1])
        label = " / ".join(parts)
        if resp and resp[0] == "critique":
            critique.append(f"🫁 {label}")
        else:
            important.append(f"🫁 {label}")

    # Cluster infectieux
    if flags["sepsis"] or flags["infection"]:
        parts = []
        if flags["sepsis"]:
            parts.append("sepsis actif")
        elif flags["infection"]:
            parts.append("infection en cours")
        if temp and temp[0] in ("critique", "limite"):
            parts.append(temp[1])
        label = " / ".join(parts)
        if flags["sepsis"]:
            critique.append(f"🦠 {label}")
        else:
            important.append(f"🦠 {label}")

    # Cluster rénal
    if flags["renal"] or diurese or creat:
        parts = []
        if diurese and diurese[0] in ("critique", "limite"):
            parts.append(diurese[1])
        if creat and creat[0] in ("critique", "limite"):
            parts.append(creat[1])
        label = " / ".join(parts) if parts else "fonction rénale altérée"
        if (diurese and diurese[0] == "critique") or (creat and creat[0] == "critique"):
            important.append(f"🧪 {label}")
        else:
            surveillance.append(f"🧪 {label}")

    # Sédation
    if flags["sedation"]:
        important.append("🧠 sédation IV — réévaluation RASS")

    # Lactate
    if lactate and lactate[0] in ("critique", "limite"):
        important.append(f"🩸 {lactate[1]} — hypoperfusion tissulaire")

    # Surveillance
    if flags["agitation"]:
        surveillance.append("🧠 agitation résiduelle")
    if not critique and not important:
        surveillance.append("✅ paramètres stables — monitoring standard")

    critique  = critique[:3]
    important = important[:3]

    return critique, important, surveillance

def build_evolution(flags, pam_level, num_analysis):
    score = 0
    if flags["choc"]:          score += 3
    if flags["sepsis"]:        score += 2
    if flags["vasopresseur"] and flags["hypotension"]: score += 2
    if flags["aggravation"]:   score += 2
    if flags["hypoxemie"]:     score += 1
    if flags["renal"]:         score += 1
    if pam_level == "basse":   score += 2
    elif pam_level == "limite": score += 1

    norad = num_analysis.get("norad")
    if norad and norad[0] == "critique":    score += 2
    elif norad and norad[0] == "limite":    score += 1

    resp = num_analysis.get("respiratoire")
    if resp and resp[0] == "critique":      score += 2
    elif resp and resp[0] == "limite":      score += 1

    lactate = num_analysis.get("lactate")
    if lactate and lactate[0] == "critique": score += 2
    elif lactate and lactate[0] == "limite": score += 1

    if score >= 7:   return "🔴 AGGRAVATION"
    elif score >= 4: return "🟠 DÉGRADATION"
    elif score >= 2: return "🟡 INDÉTERMINÉ"
    else:            return "🟢 STABLE"

def build_actions_secondaires(flags, pam_level, num_analysis):
    actions = []
    lactate = num_analysis.get("lactate")
    resp    = num_analysis.get("respiratoire")
    diurese = num_analysis.get("diurese")
    creat   = num_analysis.get("creatinine")

    if flags["choc"] and flags["sepsis"]:
        lac_str = f"— {lactate[1]}" if lactate else ""
        actions.append(f"Lactate de contrôle {lac_str} + réévaluation remplissage".strip())
    elif pam_level in ("basse", "limite") and not (flags["choc"] and flags["sepsis"]):
        actions.append("Optimisation volémie si précharge-dépendant")

    if flags["sepsis"] or flags["infection"]:
        actions.append("Réévaluation antibiothérapie — résultats hémocultures")

    if flags["ventilation"] or flags["hypoxemie"]:
        resp_str = f"({resp[1]})" if resp else ""
        actions.append(f"Contrôle gazométrique + paramètres VM {resp_str}".strip())

    if flags["sedation"]:
        actions.append("Score RASS — adapter sédation si stable hémodynamique")

    if flags["renal"] or diurese or creat:
        parts = []
        if diurese:
            parts.append(diurese[1])
        if creat:
            parts.append(creat[1])
        label = " / ".join(parts) if parts else "diurèse + créatinine"
        actions.append(f"Surveillance rénale — {label}")

    return actions[:4]

def build_numeric_panel(patient, num_analysis):
    lines = []
    order = [
        ("pam",          "🫀 PAM"),
        ("norad",        "💉 Norad"),
        ("respiratoire", "🫁 Respi"),
        ("diurese",      "🧪 Diurèse"),
        ("creatinine",   "🧪 Créat"),
        ("lactate",      "🩸 Lactate"),
        ("temperature",  "🌡️ Temp"),
    ]
    icons = {"critique": "🔴", "limite": "🟠", "ok": "🟢", "surveillance": "🟡"}
    for key, label in order:
        val = num_analysis.get(key)
        if val:
            level, desc = val
            icon = icons.get(level, "⚪")
            lines.append(f"{icon} {label} : {desc}")
    return "\n".join(lines) if lines else "  aucune valeur chiffrée détectée"

def format_icu_flow(main_problem, action_prio, critique, important,
                    surveillance, evolution, actions, numeric_panel):
    def fmt(lst):
        return "\n".join(f"  {x}" for x in lst) + "\n" if lst else "  aucun\n"

    act_str = "\n".join(f"  — {a}" for a in actions) if actions else "  — aucune action secondaire"

    return f"""
🎯 PROBLÈME PRINCIPAL
{main_problem}

━━━━━━━━━━━━━━━━━━

⚡ ACTION PRIORITAIRE
{action_prio}

━━━━━━━━━━━━━━━━━━

📊 ALERTES MONITOR ICU

🔴 CRITIQUE
{fmt(critique)}
🟠 IMPORTANT
{fmt(important)}
🟢 SURVEILLANCE
{fmt(surveillance)}
━━━━━━━━━━━━━━━━━━

📈 ÉVOLUTION : {evolution}

━━━━━━━━━━━━━━━━━━

🔢 VALEURS CLÉS
{numeric_panel}

━━━━━━━━━━━━━━━━━━

📋 ACTIONS SECONDAIRES
{act_str}

👉 ICU ENGINE V10.2
"""

# =========================================================
# ══════════════════════════════════════════════════════════
#   DISPATCH PRINCIPAL
# ══════════════════════════════════════════════════════════
# =========================================================

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ── MODE ICU FLOW ──────────────────────────────────────
    if mode == "ICU FLOW":
        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        patient  = st.session_state.patients[st.session_state.current_patient]
        extracted = extract_clinical(user_input)

        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]:
                    patient["cibles"][k].append(item)
        if not any(extracted.values()):
            patient["notes"].append(user_input)

        new_numerics = extract_numerics(user_input)
        update_numerics(patient, new_numerics)

        flags        = compute_flags(user_input, patient["cibles"])
        num_analysis = analyze_numerics(patient)
        pam_level    = detect_pam_risk(user_input, flags, num_analysis)

        main_problem  = build_main_problem(flags, pam_level, num_analysis)
        action_prio   = build_action_prioritaire(flags, pam_level, num_analysis)
        critique, important, surveillance = build_monitor_alerts_fused(flags, pam_level, num_analysis)
        evolution     = build_evolution(flags, pam_level, num_analysis)
        actions       = build_actions_secondaires(flags, pam_level, num_analysis)
        numeric_panel = build_numeric_panel(patient, num_analysis)

        answer = format_icu_flow(
            main_problem, action_prio,
            critique, important, surveillance,
            evolution, actions, numeric_panel
        )

    # ── MODE QUICK ICU ─────────────────────────────────────
    elif mode == "QUICK ICU":
        context = search_icu(user_input)
        answer  = f"⚡ **QUICK ICU**\n\n{context or 'Aucun résultat dans la base documentaire.'}\n\n👉 ICU ENGINE V10.2"

    # ── MODE PERFUSION ICU ─────────────────────────────────
    elif mode == "PERFUSION ICU":
        drug_name, weight = detect_drug_and_weight(user_input)

        if not drug_name:
            answer = (
                "💉 **PERFUSION ICU**\n\n"
                "Médicament non reconnu.\n\n"
                "Médicaments disponibles : " +
                ", ".join(sorted(set(ALIASES.values()))) +
                "\n\nEx : `noradrénaline 70kg`"
            )
        elif not weight:
            answer = (
                f"💉 **PERFUSION ICU — {drug_name.upper()}**\n\n"
                "⚠️ Poids patient non détecté.\n\n"
                f"Retape : `{drug_name} <poids>kg`\n"
                f"Ex : `{drug_name} 75kg`"
            )
        else:
            drug_data   = CONCENTRATIONS[drug_name]
            rag_context = search_icu(drug_data["fiche_rag"])
            answer      = format_perfusion_answer(drug_name, weight, drug_data, rag_context)

    # ── MODE CHECKLIST PLATEAU ─────────────────────────────
    elif mode == "CHECKLIST PLATEAU":
        proc = detect_procedure(user_input)

        if proc and proc in CHECKLISTS:
            answer = format_checklist(proc, CHECKLISTS[proc])
        else:
            available = ", ".join(sorted(CHECKLISTS.keys()))
            answer = (
                "📋 **CHECKLIST PLATEAU**\n\n"
                "Procédure non reconnue.\n\n"
                f"Procédures disponibles : {available}\n\n"
                "Ex : `intubation` · `voie centrale` · `arrêt cardiaque`"
            )

    # ── MODE IA CLINIQUE ───────────────────────────────────
    elif mode == "IA CLINIQUE":
        rag_context = search_icu(user_input)
        answer      = format_ia_clinique(user_input, rag_context)

    else:
        answer = "Mode non reconnu."

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
