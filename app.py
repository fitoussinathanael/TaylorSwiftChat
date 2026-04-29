import streamlit as st
import re
from rag_icu import search_icu

# =========================================================

# CONFIG

# =========================================================

st.set_page_config(page_title=“ICU Engine V10.4 PRO”, page_icon=“🏥”, layout=“wide”)

# CSS terrain : haute lisibilité, alertes visibles, typographie claire

st.markdown(”””

<style>
    /* Fond sombre médical */
    .stApp { background-color: #0d1117; color: #e6edf3; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

    /* Titre principal */
    h1 { color: #58a6ff !important; font-family: 'Courier New', monospace !important; }

    /* Alertes terrain */
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

    /* Blocs SBAR */
    .sbar-block {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 14px 18px; margin: 6px 0;
    }
    .sbar-label {
        color: #58a6ff; font-weight: bold; font-size: 0.85em;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* Tableau perfusion */
    .perf-row {
        display: flex; justify-content: space-between;
        padding: 8px 12px; border-bottom: 1px solid #21262d;
        font-family: 'Courier New', monospace;
    }
    .perf-row:hover { background: #21262d; }
    .perf-dose { color: #79c0ff; font-weight: bold; }
    .perf-result { color: #56d364; font-weight: bold; font-size: 1.1em; }

    /* Score badges */
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

    /* Chat messages */
    [data-testid="stChatMessage"] { background: #161b22 !important; border: 1px solid #30363d; border-radius: 8px; }

    /* Inputs */
    .stTextInput > div > div > input {
        background: #21262d !important; color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    .stSelectbox > div > div {
        background: #21262d !important; color: #e6edf3 !important;
    }
    .stNumberInput > div > div > input {
        background: #21262d !important; color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    .stButton > button {
        background: #21262d !important; color: #58a6ff !important;
        border: 1px solid #30363d !important; font-weight: bold;
    }
    .stButton > button:hover {
        background: #30363d !important; border-color: #58a6ff !important;
    }
</style>

“””, unsafe_allow_html=True)

st.title(“🏥 ICU ENGINE V10.4 PRO”)
st.caption(“ICU FLOW · PERFUSION · CHECKLIST · QUICK ICU · RAG ICU”)

# =========================================================

# SESSION STATE

# =========================================================

for key, default in [
(“messages”, []),
(“patients”, {}),
(“current_patient”, None),
(“checklist_states”, {}),
]:
if key not in st.session_state:
st.session_state[key] = default

# =========================================================

# MODE

# =========================================================

mode = st.sidebar.selectbox(
“Mode ICU”,
[“ICU FLOW”, “QUICK ICU”, “PERFUSION ICU”, “CHECKLIST PLATEAU”]
)

# =========================================================

# PATIENT (ICU FLOW uniquement)

# =========================================================

if mode == “ICU FLOW”:
st.sidebar.markdown(”—”)
st.sidebar.markdown(”## 🧠 Patients”)
new_patient = st.sidebar.text_input(“Créer patient”, key=“new_pt”)
if st.sidebar.button(“➕ Ajouter”) and new_patient.strip():
name = new_patient.strip()
if name not in st.session_state.patients:
st.session_state.patients[name] = {“notes”: []}
st.session_state.current_patient = name
st.sidebar.success(f”✅ {name}”)

```
if st.session_state.patients:
    st.session_state.current_patient = st.sidebar.selectbox(
        "Patient actif",
        list(st.session_state.patients.keys())
    )
    if st.session_state.current_patient:
        st.sidebar.markdown(
            f"<span class='score-badge badge-blue'>👤 {st.session_state.current_patient}</span>",
            unsafe_allow_html=True
        )
```

# =========================================================

# UTILS

# =========================================================

def safe_rag(query: str):
“”“RAG avec fallback explicite et log d’erreur.”””
if not query or not query.strip():
return None
try:
res = search_icu(query.strip())
if isinstance(res, dict) and res:
return res
return None
except Exception as e:
st.sidebar.warning(f”⚠️ RAG indisponible : {e}”)
return None

def compute_map(sys: int, dia: int) -> float:
“””
PAM = (PAS + 2×PAD) / 3
Formule correcte pour pression artérielle moyenne.
“””
return round((sys + 2 * dia) / 3, 1)

def extract_bp(text: str):
“”“Extrait PAS/PAD depuis texte libre. Retourne (sys, dia) ou (None, None).”””
# Formats acceptés : 120/80, 120 / 80, 85/50
match = re.search(r’\b(\d{2,3})\s*/\s*(\d{2,3})\b’, text)
if match:
return int(match.group(1)), int(match.group(2))
return None, None

def severity_badge(level: str) -> str:
mapping = {
“CRITIQUE”: “badge-red”,
“SÉVÈRE”: “badge-orange”,
“MODÉRÉ”: “badge-yellow”,
“STABLE”: “badge-green”,
}
cls = mapping.get(level, “badge-blue”)
icons = {“CRITIQUE”: “🔴”, “SÉVÈRE”: “🟠”, “MODÉRÉ”: “🟡”, “STABLE”: “🟢”}
icon = icons.get(level, “⚪”)
return f”<span class='score-badge {cls}'>{icon} {level}</span>”

def alert_block(text: str, level: str) -> str:
cls_map = {
“CRITIQUE”: “alert-critique”,
“SÉVÈRE”: “alert-severe”,
“MODÉRÉ”: “alert-modere”,
“OK”: “alert-ok”,
}
return f”<div class=’{cls_map.get(level, ‘alert-modere’)}’>{text}</div>”

# =========================================================

# ICU FLOW — version terrain

# =========================================================

def build_flow(text: str) -> str:
t = text.lower()

```
# --- Scores ---
resp_score = 0
if any(x in t for x in ["dyspnée", "dysp", "polypnée", "bradypnée"]):
    resp_score += 1
if any(x in t for x in ["hypox", "désaturation", "sat"]):
    resp_score += 2
if any(x in t for x in ["84%", "85%", "86%", "87%", "88%", "89%", "90%"]):
    resp_score += 2
if any(x in t for x in ["intubation", "ventilation", "vni", "o2 haut débit"]):
    resp_score += 1

shock_score = 0
sys_val, dia_val = extract_bp(text)
if sys_val is not None and sys_val < 90:
    shock_score += 3
elif sys_val is not None and sys_val < 100:
    shock_score += 1
if any(x in t for x in ["hypotension", "choc", "collapsus"]):
    shock_score += 2
if any(x in t for x in ["norad", "noradrenaline", "noradrénaline", "vasopresseur"]):
    shock_score += 2
if any(x in t for x in ["tachycardie", "bradycardie", "arythmie", "fa "]):
    shock_score += 1

neuro_score = 0
if any(x in t for x in ["confusion", "agitation", "glasgow", "convulsion", "coma", "somnolence"]):
    neuro_score += 2
if any(x in t for x in ["gcs", "glasgow"]):
    # Cherche Glasgow score
    gcs_match = re.search(r'(?:gcs|glasgow)\s*[=:à]?\s*(\d{1,2})', t)
    if gcs_match:
        gcs = int(gcs_match.group(1))
        if gcs <= 8:
            neuro_score += 3
        elif gcs <= 12:
            neuro_score += 1

sofa_like = resp_score + shock_score + neuro_score

# --- Gravité ---
if sofa_like >= 6:
    severity = "CRITIQUE"
elif sofa_like >= 4:
    severity = "SÉVÈRE"
elif sofa_like >= 2:
    severity = "MODÉRÉ"
else:
    severity = "STABLE"

# --- PAM ---
pam_str = "N/A"
pam_alert = ""
if sys_val and dia_val:
    pam = compute_map(sys_val, dia_val)
    pam_str = f"{pam} mmHg"
    if pam < 65:
        pam_alert = alert_block(f"⚠️ PAM CRITIQUE : {pam} mmHg — Objectif ≥ 65 mmHg", "CRITIQUE")
    elif pam < 70:
        pam_alert = alert_block(f"⚠️ PAM BASSE : {pam} mmHg — Surveiller", "MODÉRÉ")
    else:
        pam_alert = alert_block(f"✅ PAM : {pam} mmHg — Dans les cibles", "OK")

# --- Alertes actives ---
alerts_html = ""
if resp_score >= 3:
    alerts_html += alert_block("🫁 ALERTE RESPIRATOIRE — Évaluer ventilation / O2 immédiatement", "CRITIQUE")
elif resp_score >= 1:
    alerts_html += alert_block("🫁 Surveillance respiratoire renforcée", "MODÉRÉ")

if shock_score >= 4:
    alerts_html += alert_block("🫀 ALERTE CHOC — Remplissage / vasopresseurs / médecin URGENT", "CRITIQUE")
elif shock_score >= 2:
    alerts_html += alert_block("🫀 Instabilité hémodynamique — Surveillance TA rapprochée", "SÉVÈRE")

if neuro_score >= 3:
    alerts_html += alert_block("🧠 ALERTE NEUROLOGIQUE — Glasgow bas / Convulsion / Coma", "CRITIQUE")

if severity == "CRITIQUE":
    alerts_html += alert_block("🚨 PATIENT CRITIQUE — Appeler médecin senior / Préparer matériel réanimation", "CRITIQUE")

# --- Cibles détectées ---
targets = []
if resp_score > 0:
    targets.append("🫁 Respiratoire")
if shock_score > 0:
    targets.append("🫀 Hémodynamique")
if neuro_score > 0:
    targets.append("🧠 Neurologique")
if any(x in t for x in ["sepsis", "infection", "fièvre", "antibiotique"]):
    targets.append("🦠 Infectieux")
if any(x in t for x in ["douleur", "analgésie", "opioïde"]):
    targets.append("💊 Analgésie")

targets_str = " | ".join(targets) if targets else "Évaluation en cours"

# --- Assessment ---
assessments = []
if resp_score >= 2 and shock_score >= 2:
    assessments.append("Détresse respiratoire + instabilité hémodynamique")
elif resp_score >= 2:
    assessments.append("Détresse respiratoire prédominante")
elif shock_score >= 2:
    assessments.append("Instabilité hémodynamique prédominante")
elif neuro_score >= 2:
    assessments.append("Altération neurologique")
else:
    assessments.append("Surveillance clinique standard")
assessment = " — ".join(assessments)

# Construction HTML
patient_label = f" — {st.session_state.current_patient}" if st.session_state.current_patient else ""

return f"""
```

<h3>🧠 ICU FLOW{patient_label}</h3>

<b>🎯 CIBLES :</b> {targets_str}<br><br>

{severity_badge(severity)}
<span class='score-badge badge-blue'>RESP {resp_score}</span>
<span class='score-badge badge-blue'>CHOC {shock_score}</span>
<span class='score-badge badge-blue'>NEURO {neuro_score}</span>
<span class='score-badge badge-blue'>SOFA-L {sofa_like}</span>
<br><br>

{pam_alert}
{alerts_html}

<br>
<div class='sbar-block'>
<div class='sbar-label'>S — Situation</div>
<div>{text}</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>B — Background</div>
<div>Patient en réanimation. Surveillance continue. Dossier ICU actif.</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>A — Assessment</div>
<div>{assessment}</div>
<div>📊 TA : {f"{sys_val}/{dia_val} mmHg" if sys_val else "Non renseignée"} | PAM : {pam_str}</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>R — Recommendation</div>
<div>
{'⚠️ Contacter médecin senior URGENT<br>' if severity == 'CRITIQUE' else ''}
• Monitorage continu (TA, SpO2, FC, FR)<br>
• Réévaluation clinique dans {'15 min' if severity in ['CRITIQUE', 'SÉVÈRE'] else '1h'}<br>
• Adapter thérapeutique selon évolution<br>
• Tracer dans dossier patient
</div>
</div>
"""

# =========================================================

# QUICK ICU — avec fallback propre

# =========================================================

def quick(text: str) -> str:
rag = safe_rag(text)

```
if not rag:
    # Fallback : base locale minimale
    fallback_db = {
        "noradrenaline": {"classe": "Catécholamine", "usage": "Choc septique / vasoplégique", "effets": "Vasoconstriction, ↑RVS", "surveillance": "TA invasive, FC, diurèse, extrémités", "points_icu": "Objectif PAM ≥ 65 mmHg"},
        "propofol": {"classe": "Hypnotique IV", "usage": "Sédation ventilés", "effets": "Hypnose, ↓PA, apnée", "surveillance": "PA, FR, Triglyc si >3j", "points_icu": "PROPOFOL SYNDROME si >4mg/kg/h prolongé"},
        "midazolam": {"classe": "Benzodiazépine", "usage": "Sédation / anxiolyse / épilepsie", "effets": "Sédation, amnésie, dépression respi", "surveillance": "Score sédation (RASS), FR, PA", "points_icu": "Accumulation en IHC/IRC — titrer"},
        "ketamine": {"classe": "Anesthésique dissociatif", "usage": "Induction ISR / analgésie", "effets": "Bronchodilatation, ↑PA, hallucinations", "surveillance": "PA, SpO2, agitation au réveil", "points_icu": "Choix idéal si bronchospasme ou instabilité hémodynamique"},
        "furosemide": {"classe": "Diurétique de l'anse", "usage": "Surcharge hydrique / OAP", "effets": "Diurèse forcée, hypokaliémie", "surveillance": "Ionogramme, diurèse, PA", "points_icu": "Surveiller kaliémie — risque hypokaliémie"},
    }
    key = text.lower().strip()
    for drug, info in fallback_db.items():
        if drug in key or key in drug:
            rag = info
            break

if not rag:
    return f"""<div class='alert-modere'>
```

⚡ <b>QUICK ICU</b> — <b>{text.upper()}</b><br><br>
❌ Aucune donnée trouvée dans la base RAG ni en base locale.<br>
💡 Vérifier : orthographe, DCI complète, ou consulter Vidal/Thériaque.

</div>"""

```
return f"""
```

<h3>⚡ QUICK ICU — {text.upper()}</h3>

<div class='sbar-block'>
<div class='sbar-label'>Classe</div>
<div>{rag.get('classe', '—')}</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>Usage ICU</div>
<div>{rag.get('usage', '—')}</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>Effets principaux</div>
<div>{rag.get('effets', '—')}</div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>🔍 Surveillance infirmière</div>
<div><b>{rag.get('surveillance', '—')}</b></div>
</div>

<div class='sbar-block'>
<div class='sbar-label'>⚠️ Points clés ICU</div>
<div>{rag.get('points_icu', '—')}</div>
</div>
"""

# =========================================================

# PERFUSION ICU — Formulaire dédié (zéro crash)

# =========================================================

DRUGS = {
“noradrenaline”: {
“conc_mg_per_ml”: 0.08,
“unit”: “µg/kg/min”,
“steps”: [0.05, 0.1, 0.15, 0.2, 0.3, 0.5],
“target”: “PAM ≥ 65 mmHg”,
“alert”: “⚠️ Voie centrale dédiée — surveiller extrémités”,
“bag”: “Seringue 50mL : 4mg dans 50mL NaCl 0.9% = 0.08mg/mL”
},
“propofol”: {
“conc_mg_per_ml”: 10.0,
“unit”: “mg/kg/h”,
“steps”: [1, 2, 3, 4, 5],
“target”: “RASS -2 à 0”,
“alert”: “⚠️ Max 4mg/kg/h — Triglyc si >72h”,
“bag”: “Flacon 200mg/20mL (10mg/mL) prêt à l’emploi”
},
“midazolam”: {
“conc_mg_per_ml”: 1.0,
“unit”: “mg/kg/h”,
“steps”: [0.02, 0.05, 0.1, 0.15, 0.2],
“target”: “RASS -2 à 0”,
“alert”: “⚠️ Accumulation IHC/IRC — titrer progressivement”,
“bag”: “Seringue 50mL : 50mg dans 50mL NaCl 0.9% = 1mg/mL”
},
“morphine”: {
“conc_mg_per_ml”: 1.0,
“unit”: “mg/kg/h”,
“steps”: [0.01, 0.02, 0.03, 0.05],
“target”: “BPS ≤ 5 / NRS ≤ 3”,
“alert”: “⚠️ Surveiller FR, SpO2 — Naloxone disponible”,
“bag”: “Seringue 50mL : 50mg dans 50mL NaCl 0.9% = 1mg/mL”
},
“dobutamine”: {
“conc_mg_per_ml”: 1.0,
“unit”: “µg/kg/min”,
“steps”: [2, 5, 7, 10, 15, 20],
“target”: “DC/IC — réponse clinique”,
“alert”: “⚠️ Risque tachycardie / arythmie”,
“bag”: “Seringue 50mL : 250mg dans 50mL G5% = 5mg/mL”
},
“ketamine”: {
“conc_mg_per_ml”: 1.0,
“unit”: “mg/kg/h”,
“steps”: [0.1, 0.2, 0.3, 0.5],
“target”: “Analgésie / sédation légère”,
“alert”: “⚠️ Associer benzodiazépine si agitation — surveiller PA”,
“bag”: “Seringue 50mL : 50mg dans 50mL NaCl 0.9% = 1mg/mL”
},
}

DRUG_ALIASES = {
“nora”: “noradrenaline”, “norad”: “noradrenaline”,
“noradrénaline”: “noradrenaline”,
“propofol”: “propofol”, “diprivan”: “propofol”,
“midazolam”: “midazolam”, “hypnovel”: “midazolam”,
“morphine”: “morphine”, “chlorhydrate”: “morphine”,
“dobu”: “dobutamine”, “dobutamine”: “dobutamine”,
“kétamine”: “ketamine”, “ketamine”: “ketamine”, “ketalar”: “ketamine”,
}

def calc_rate(dose: float, weight: float, conc: float, unit: str) -> float:
“””
Calcule le débit seringue (mL/h) selon l’unité.
- µg/kg/min : dose(µg/kg/min) × poids(kg) × 60 / (conc(mg/mL) × 1000)
- mg/kg/h   : dose(mg/kg/h) × poids(kg) / conc(mg/mL)
“””
if unit == “µg/kg/min”:
return round((dose * weight * 60) / (conc * 1000), 2)
elif unit == “mg/kg/h”:
return round((dose * weight) / conc, 2)
return 0.0

def perfusion_ui():
“”“Interface formulaire dédiée — remplace le parsing regex fragile.”””
st.markdown(”### 💉 PERFUSION ICU”)
st.markdown(“Calcul de débit seringue électrique — entrer poids et médicament”)

```
col1, col2 = st.columns([1, 1])

with col1:
    weight = st.number_input(
        "⚖️ Poids patient (kg)",
        min_value=20.0, max_value=200.0,
        value=70.0, step=1.0,
        key="perf_weight"
    )
    drug_choice = st.selectbox(
        "💊 Médicament",
        options=list(DRUGS.keys()),
        format_func=lambda x: x.upper(),
        key="perf_drug"
    )

drug = DRUGS[drug_choice]

with col2:
    st.markdown(f"**Préparation :** {drug['bag']}")
    st.markdown(f"**Unité :** `{drug['unit']}`")
    st.markdown(f"**Cible :** {drug['target']}")
    st.markdown(
        alert_block(drug['alert'], "MODÉRÉ"),
        unsafe_allow_html=True
    )

st.markdown("---")
st.markdown("**📊 Tableau débit (mL/h)**")

# Tableau de débits pour toutes les doses préréglées
header_html = """
<div style='display:grid; grid-template-columns:1fr 1fr 1fr; 
     background:#21262d; padding:8px 12px; border-radius:6px 6px 0 0;
     font-weight:bold; color:#8b949e; font-size:0.85em;'>
    <span>DOSE</span>
    <span>DÉBIT CALCULÉ</span>
    <span>VÉRIF</span>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

rows_html = ""
for dose in drug["steps"]:
    rate = calc_rate(dose, weight, drug["conc_mg_per_ml"], drug["unit"])
    # Indicateur visuel du débit
    indicator = "🟢" if rate < 20 else ("🟡" if rate < 40 else "🔴")
    rows_html += f"""
    <div style='display:grid; grid-template-columns:1fr 1fr 1fr;
         padding:10px 12px; border-bottom:1px solid #21262d;
         font-family:Courier New,monospace;'>
        <span style='color:#79c0ff; font-weight:bold;'>{dose} {drug['unit']}</span>
        <span style='color:#56d364; font-weight:bold; font-size:1.15em;'>{rate} mL/h</span>
        <span>{indicator}</span>
    </div>
    """
st.markdown(rows_html, unsafe_allow_html=True)

# Dose personnalisée
st.markdown("---")
st.markdown("**🧮 Dose personnalisée**")
custom_dose = st.number_input(
    f"Dose ({drug['unit']})",
    min_value=0.001, max_value=100.0,
    value=float(drug["steps"][0]),
    step=0.01,
    format="%.3f",
    key="custom_dose"
)
custom_rate = calc_rate(custom_dose, weight, drug["conc_mg_per_ml"], drug["unit"])
st.markdown(
    f"<div class='alert-ok'>💉 {custom_dose} {drug['unit']} × {weight} kg → <b style='font-size:1.3em;'>{custom_rate} mL/h</b></div>",
    unsafe_allow_html=True
)

# RAG enrichissement
rag = safe_rag(drug_choice)
if rag:
    with st.expander("📖 Fiche RAG médicament"):
        st.markdown(f"**Classe :** {rag.get('classe', '—')}")
        st.markdown(f"**Usage :** {rag.get('usage', '—')}")
        st.markdown(f"**Surveillance :** {rag.get('surveillance', '—')}")
        st.markdown(f"**Points ICU :** {rag.get('points_icu', '—')}")
```

# =========================================================

# CHECKLIST PLATEAU — Checkboxes interactives avec état

# =========================================================

CHECKLISTS = {
“Intubation (ISR)”: {
“🔧 MATÉRIEL”: [
“Laryngoscope vérifié + lame adaptée”,
“Sondes d’intubation 7.0 / 7.5 / 8.0”,
“Mandrin béquillé”,
“Seringue 10 mL pour ballonnet”,
“Ambu + masque adapté au patient”,
“Capnographe connecté et prêt”,
“Aspiration active (sonde Yankauer)”,
“Oxygène ouvert débit max”,
“Monitoring : TA, SpO2, FC, scope”,
],
“💊 MÉDICAMENTS”: [
“Hypnotique préparé (Étomidate / Kétamine / Propofol)”,
“Curare préparé (Succinylcholine / Rocuronium)”,
“Noradrénaline prête (choc post-intubation)”,
“Atropine disponible (bradycardie vagale)”,
],
“✅ VÉRIFICATIONS FINALES”: [
“VVP / VVC fonctionnelle vérifiée”,
“Monitoring actif et visible”,
“Patient en position optimale (proclive 20°)”,
“Plan B défini : VMI / Fastrach / Cricothyroïdotomie”,
“Équipe prévenue (médecin senior présent)”,
“Accord IADE / anesthésiste si disponible”,
],
“🚨 POST-INTUBATION”: [
“Capnographie confirmée (courbe ETCO2)”,
“Auscultation bilatérale”,
“RX thorax commandée”,
“Sédation démarrée”,
“Ventilateur paramétré”,
],
},
“Pose VVC”: {
“🔧 MATÉRIEL”: [
“Kit VVC adapté (taille / lumières)”,
“Échographie vasculaire disponible”,
“Champ stérile large”,
“Désinfectant (Bétadine / Chlorhexidine)”,
“Anesthésie locale (Lidocaïne 1%)”,
“Seringues + aiguilles de différents calibres”,
“Sutures + pansement occlusif”,
],
“✅ VÉRIFICATIONS”: [
“Bilan coagulation vérifié (TP, TCA, plaquettes)”,
“Consentement tracé si possible”,
“Position patient adaptée (Trendelenburg si VJI/SC)”,
“Monitoring actif”,
“Radiologue prévenu pour RX de contrôle”,
],
“🚨 SURVEILLANCE POST-POSE”: [
“RX thorax réalisée”,
“Pas de pneumothorax confirmé”,
“Retour veineux vérifier (aspiration sang)”,
“Pansement occlusif propre”,
“Heure de pose et opérateur tracés”,
],
},
“Transfert patient critique”: {
“💊 MÉDICAMENTS”: [
“Seringues électriques rechargées (autonomie ≥1h)”,
“Stock médicaments d’urgence emporté”,
“Pousse-seringues de transport prêts”,
],
“🔧 ÉQUIPEMENT”: [
“Ventilateur de transport prêt + O2 suffisant”,
“Monitoring portable actif”,
“Aspiration portative”,
“Défibrillateur disponible”,
“Ambu + masque”,
],
“✅ AVANT DÉPART”: [
“Dossier médical complet emporté”,
“Transmission verbale faite au médecin receveur”,
“Famille informée si possible”,
“Équipe de transport identifiée”,
“Numéro SAMU/SMUR si transport externe”,
],
},
}

def checklist_ui():
st.markdown(”### 📋 CHECKLIST PLATEAU”)

```
checklist_choice = st.selectbox(
    "Type de checklist",
    options=list(CHECKLISTS.keys()),
    key="checklist_type"
)

checklist = CHECKLISTS[checklist_choice]

# Init states pour cette checklist
ck_key = f"ck_{checklist_choice}"
if ck_key not in st.session_state.checklist_states:
    st.session_state.checklist_states[ck_key] = {}

total = sum(len(v) for v in checklist.values())
checked = 0

for section, items in checklist.items():
    st.markdown(f"**{section}**")
    for item in items:
        item_key = f"{ck_key}_{item}"
        val = st.checkbox(
            item,
            key=item_key,
            value=st.session_state.checklist_states[ck_key].get(item, False)
        )
        st.session_state.checklist_states[ck_key][item] = val
        if val:
            checked += 1
    st.markdown("")

# Barre de progression
progress = checked / total if total > 0 else 0
st.progress(progress)

if checked == total:
    st.markdown(
        alert_block(f"✅ CHECKLIST COMPLÈTE — {checked}/{total} éléments validés — Procédure autorisée", "OK"),
        unsafe_allow_html=True
    )
elif checked >= total * 0.8:
    st.markdown(
        alert_block(f"⚠️ Presque prête — {checked}/{total} éléments — Vérifier les points manquants", "MODÉRÉ"),
        unsafe_allow_html=True
    )
else:
    st.markdown(
        alert_block(f"❌ {checked}/{total} éléments — Checklist incomplète", "SÉVÈRE"),
        unsafe_allow_html=True
    )

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Réinitialiser la checklist"):
        st.session_state.checklist_states[ck_key] = {}
        st.rerun()
with col2:
    if st.button("✅ Valider et tracer"):
        st.success(f"✅ Checklist '{checklist_choice}' tracée — {checked}/{total} éléments validés")
```

# =========================================================

# DISPATCH PRINCIPAL

# =========================================================

# Modes avec interface dédiée (pas de chat)

if mode == “PERFUSION ICU”:
perfusion_ui()
st.stop()

if mode == “CHECKLIST PLATEAU”:
checklist_ui()
st.stop()

# Modes chat (ICU FLOW + QUICK ICU)

for msg in st.session_state.messages:
with st.chat_message(msg[“role”]):
st.markdown(msg[“content”], unsafe_allow_html=True)

user_input = st.chat_input(“Entrée ICU… (ex: ‘patient TA 85/50 dyspnée norad’ ou ‘propofol’)”)

if user_input:
st.session_state.messages.append({“role”: “user”, “content”: user_input})
with st.chat_message(“user”):
st.markdown(user_input)

```
if mode == "ICU FLOW":
    answer = build_flow(user_input)
elif mode == "QUICK ICU":
    # Résoudre alias médicament
    resolved = DRUG_ALIASES.get(user_input.lower().strip(), user_input)
    answer = quick(resolved)
else:
    answer = "⚠️ Mode inconnu"

with st.chat_message("assistant"):
    st.markdown(answer, unsafe_allow_html=True)

st.session_state.messages.append({"role": "assistant", "content": answer})
```
