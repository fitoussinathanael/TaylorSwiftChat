import streamlit as st
from datetime import datetime
import uuid

# =========================

# CSS GLOBAL — STYLE APP IPHONE

# =========================

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fond général */
.stApp {
    background-color: #0f0f14;
    color: #f0f0f5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #16161e;
    border-right: 1px solid #2a2a3a;
}

section[data-testid="stSidebar"] * {
    color: #d0d0e0 !important;
}

/* Titres */
h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    color: #ffffff;
}

/* Cards personnalisées */
.juri-card {
    background: linear-gradient(135deg, #1a1a28 0%, #1e1e2e 100%);
    border: 1px solid #2e2e45;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

.juri-card-urgent {
    background: linear-gradient(135deg, #2a1a1a 0%, #2e1e1e 100%);
    border: 1px solid #8b2020;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 4px 24px rgba(139,32,32,0.2);
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #1e1e30 0%, #22223a 100%);
    border: 1px solid #3a3a55;
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.kpi-number {
    font-size: 48px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}

.kpi-label {
    font-size: 13px;
    color: #8888aa;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Mono', monospace;
}

/* Bouton urgence */
.btn-urgence {
    background: linear-gradient(135deg, #c0392b, #e74c3c);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 16px 24px;
    font-size: 16px;
    font-weight: 700;
    width: 100%;
    cursor: pointer;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 20px rgba(231,76,60,0.4);
}

/* Badges */
.badge-high {
    background: #e74c3c;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

.badge-medium {
    background: #e67e22;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

.badge-low {
    background: #27ae60;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* Séparateur stylisé */
.juri-divider {
    border: none;
    border-top: 1px solid #2a2a3a;
    margin: 20px 0;
}

/* Timeline event */
.timeline-event {
    background: #1a1a28;
    border-left: 3px solid #5555aa;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #c0c0d8;
    font-family: 'DM Mono', monospace;
}

/* Shadow mode banner */
.shadow-active-banner {
    background: linear-gradient(90deg, #1a0a2e, #2a1a4e);
    border: 1px solid #7755aa;
    border-radius: 12px;
    padding: 10px 18px;
    color: #cc99ff;
    font-weight: 600;
    text-align: center;
    margin-bottom: 16px;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background-color: #1e1e2e !important;
    border: 1px solid #3a3a55 !important;
    border-radius: 12px !important;
    color: #f0f0f5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #5555cc, #8844ee);
    border-radius: 10px;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1e1e2e !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* Boutons Streamlit */
.stButton > button {
    background: linear-gradient(135deg, #2a2a45, #35355a) !important;
    color: #e0e0f5 !important;
    border: 1px solid #4a4a70 !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #35355a, #444470) !important;
    border-color: #6666aa !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(100,100,200,0.3) !important;
}

/* Métriques */
[data-testid="stMetric"] {
    background: #1e1e2e;
    border-radius: 16px;
    padding: 16px;
    border: 1px solid #2e2e45;
}

/* Success / Warning / Error boxes */
.stSuccess {
    background: #0d2a1a !important;
    border: 1px solid #1a6a3a !important;
    border-radius: 12px !important;
}
.stWarning {
    background: #2a1a0a !important;
    border: 1px solid #6a3a0a !important;
    border-radius: 12px !important;
}
.stError {
    background: #2a0d0d !important;
    border: 1px solid #6a1a1a !important;
    border-radius: 12px !important;
}
.stInfo {
    background: #0d1a2a !important;
    border: 1px solid #1a3a6a !important;
    border-radius: 12px !important;
}
</style>

“””, unsafe_allow_html=True)

# =========================

# INIT SESSION STATE

# =========================

if “clients” not in st.session_state:
st.session_state.clients = {}

if “dossiers” not in st.session_state:
st.session_state.dossiers = {}

if “shadow_mode” not in st.session_state:
st.session_state.shadow_mode = False

if “selected_client_id” not in st.session_state:
st.session_state.selected_client_id = None

if “client_step” not in st.session_state:
st.session_state.client_step = 1

if “client_form_data” not in st.session_state:
st.session_state.client_form_data = {}

if “email_drafts” not in st.session_state:
st.session_state.email_drafts = {}

# =========================

# IA SIMULÉE (MVP)

# =========================

def ai_structurate(text):
return {
“resume”: f”Résumé structuré de la demande : {text[:120]}…”,
“type”: “Droit du travail (détecté)”,
“urgence”: “MEDIUM”,
“priority”: “🟠 PRIORITÉ MOYENNE”,
“risques”: [
“Risque de litige”,
“Délai légal à vérifier”
],
“pieces”: [
“Contrat de travail”,
“Emails”,
“Courriers reçus”
],
“deadlines”: [
“Prescription potentielle dans 12 jours”,
“Réponse employeur attendue sous 5 jours”
],
“flags”: [
“⚠️ Pièces manquantes”,
“🚨 Vérifier délai légal”
],
“confidence”: 82
}

def ai_analyse_document(file_name):
return f””“Analyse du document : {file_name}

— Type détecté : PDF juridique
— Points clés : clauses contractuelles détectées
— Risques : à vérifier par avocat
— Synthèse : document ajouté au dossier”””

# =========================

# UTILITAIRE TIMELINE

# =========================

def add_event(dossier_id, message):
if dossier_id in st.session_state.dossiers:
st.session_state.dossiers[dossier_id][“timeline”].append({
“time”: datetime.now().strftime(”%H:%M”),
“message”: message
})

# =========================

# UTILITAIRES CRÉATION

# =========================

def create_client(nom, prenom, societe, email, tel):
client_id = str(uuid.uuid4())
st.session_state.clients[client_id] = {
“nom”: nom,
“prenom”: prenom,
“societe”: societe,
“email”: email,
“tel”: tel,
“created_at”: datetime.now(),
“dossiers”: []
}
return client_id

def create_dossier(client_id, description, source):
dossier_id = str(uuid.uuid4())
analysis = ai_structurate(description)

```
st.session_state.dossiers[dossier_id] = {
    "client_id": client_id,
    "description": description,
    "source": source,
    "analysis": analysis,
    "status": "NEW",
    "files": [],
    "created_at": datetime.now(),
    "shadow_local": False,
    "workflow_stage": 1,
    "workflow_steps": [
        "Intake",
        "Analyse",
        "Pièces",
        "Stratégie",
        "Action",
        "Clôture"
    ],
    "tasks": [
        {"label": "Contacter client", "done": False},
        {"label": "Demander pièces manquantes", "done": False},
        {"label": "Analyser documents", "done": False},
        {"label": "Préparer rendez-vous", "done": False}
    ],
    "timeline": [
        {
            "time": datetime.now().strftime("%H:%M"),
            "message": "📁 Dossier créé"
        },
        {
            "time": datetime.now().strftime("%H:%M"),
            "message": "🧠 Analyse IA générée"
        }
    ]
}

if client_id in st.session_state.clients:
    st.session_state.clients[client_id]["dossiers"].append(dossier_id)

return dossier_id
```

# =========================

# HELPER : BADGE URGENCE

# =========================

def urgence_badge(level):
if level == “HIGH”:
return ‘<span class="badge-high">🔴 URGENT</span>’
elif level == “MEDIUM”:
return ‘<span class="badge-medium">🟠 MOYEN</span>’
else:
return ‘<span class="badge-low">🟢 BAS</span>’

# =========================

# CONFIG PAGE

# =========================

st.set_page_config(
page_title=“JuriEngine”,
page_icon=“⚖️”,
layout=“wide”
)

# =========================

# SIDEBAR

# =========================

with st.sidebar:
st.markdown(”””
<div style='padding: 8px 0 20px 0;'>
<div style='font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;'>
⚖️ JuriEngine
</div>
<div style='font-size: 11px; color: #6666aa; font-family: DM Mono, monospace; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px;'>
Orchestration Intelligente
</div>
</div>
“””, unsafe_allow_html=True)

```
mode = st.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Client",
        "⚖️ Avocat",
        "🤖 Agent IA",
        "🗂️ Archives",
        "👥 Clients"
    ],
    label_visibility="collapsed"
)

st.markdown("<hr style='border-color:#2a2a3a; margin: 16px 0;'>", unsafe_allow_html=True)

# Shadow Mode
st.session_state.shadow_mode = st.toggle(
    "👻 Shadow Mode",
    value=st.session_state.shadow_mode
)

if st.session_state.shadow_mode:
    st.markdown("""
    <div style='background: linear-gradient(135deg,#2a1a4e,#1a0a2e);
                border: 1px solid #7755aa; border-radius: 10px;
                padding: 10px 14px; color: #cc99ff; font-size: 13px;
                font-weight: 600; text-align: center; margin-top: 8px;'>
        👻 SHADOW MODE ACTIF
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background: #1a1a28; border: 1px solid #2a2a3a; border-radius: 10px;
                padding: 10px 14px; color: #555577; font-size: 13px;
                text-align: center; margin-top: 8px;'>
        Shadow Mode OFF
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color:#2a2a3a; margin: 16px 0;'>", unsafe_allow_html=True)

# Alertes
st.markdown("**🔔 Alertes Cabinet**")

urgent_count = sum(
    1 for d in st.session_state.dossiers.values()
    if d["analysis"]["urgence"] == "HIGH"
)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""
    <div style='background:#2a0d0d; border:1px solid #6a1a1a; border-radius:10px;
                padding:10px; text-align:center;'>
        <div style='font-size:22px; font-weight:700; color:#e74c3c;'>{urgent_count}</div>
        <div style='font-size:10px; color:#aa4444; text-transform:uppercase;
                    font-family: DM Mono, monospace;'>Urgents</div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown(f"""
    <div style='background:#0d1a2a; border:1px solid #1a3a6a; border-radius:10px;
                padding:10px; text-align:center;'>
        <div style='font-size:22px; font-weight:700; color:#5599ee;'>{len(st.session_state.dossiers)}</div>
        <div style='font-size:10px; color:#4477aa; text-transform:uppercase;
                    font-family: DM Mono, monospace;'>Dossiers</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bouton urgence cabinet — toujours visible dans la sidebar
st.markdown("**🚨 Contact Cabinet**")
if st.button("🚨 URGENCE — Appeler le Cabinet", key="sidebar_urgence"):
    st.toast("🚨 Appel d'urgence déclenché — Cabinet notifié", icon="🚨")
    # Log dans tous les dossiers ouverts
    for d_id in st.session_state.dossiers:
        add_event(d_id, "🚨 Appel urgence cabinet déclenché")
```

# =========================

# DASHBOARD

# =========================

if mode == “🏠 Dashboard”:

```
st.markdown("## 🏠 Dashboard JuriEngine")

if st.session_state.shadow_mode:
    st.markdown("""
    <div class='shadow-active-banner'>👻 Shadow Mode activé — L'IA écoute et structure en arrière-plan</div>
    """, unsafe_allow_html=True)

# KPI Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-number' style='color:#5599ee;'>{len(st.session_state.clients)}</div>
        <div class='kpi-label'>Clients</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-number' style='color:#aa77ee;'>{len(st.session_state.dossiers)}</div>
        <div class='kpi-label'>Dossiers</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-number' style='color:#e74c3c;'>{urgent_count}</div>
        <div class='kpi-label'>Urgents</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    shadow_color = "#cc99ff" if st.session_state.shadow_mode else "#555577"
    shadow_label = "ON" if st.session_state.shadow_mode else "OFF"
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-number' style='color:{shadow_color};'>{shadow_label}</div>
        <div class='kpi-label'>Shadow Mode</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Barre de statut globale
if urgent_count > 0:
    st.markdown("""
    <div style='background: linear-gradient(90deg,#2a0808,#3a1010); border:1px solid #8b2020;
                border-radius:14px; padding:14px 20px; color:#ff6666; font-weight:600;
                font-size:15px; margin-bottom:20px;'>
        🔴 Attention : des dossiers urgents nécessitent une action immédiate
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background: linear-gradient(90deg,#082a14,#0f3a1e); border:1px solid #1a6a3a;
                border-radius:14px; padding:14px 20px; color:#55cc88; font-weight:600;
                font-size:15px; margin-bottom:20px;'>
        ✅ Aucune urgence en cours — Tout est sous contrôle
    </div>
    """, unsafe_allow_html=True)

# Dossiers récents
st.markdown("### 📌 Dossiers récents")

if not st.session_state.dossiers:
    st.markdown("""
    <div class='juri-card' style='text-align:center; color:#555577; padding:40px;'>
        <div style='font-size:40px; margin-bottom:10px;'>📂</div>
        <div style='font-size:16px;'>Aucun dossier pour le moment</div>
        <div style='font-size:13px; margin-top:4px; color:#444466;'>Les nouveaux dossiers apparaîtront ici</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for d_id, dossier in list(st.session_state.dossiers.items())[-5:]:
        client = st.session_state.clients.get(dossier["client_id"], {})
        urgence = dossier["analysis"]["urgence"]
        card_class = "juri-card-urgent" if urgence == "HIGH" else "juri-card"
        badge_html = urgence_badge(urgence)

        st.markdown(f"""
        <div class='{card_class}'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                <div style='font-size:16px; font-weight:700; color:#ffffff;'>
                    👤 {client.get('nom','')} {client.get('prenom','')}
                </div>
                {badge_html}
            </div>
            <div style='color:#9999bb; font-size:13px; margin-bottom:4px;'>
                📌 {dossier['analysis']['type']}
            </div>
            <div style='display:flex; gap:12px; margin-top:10px;'>
                <div style='background:#1a1a35; border-radius:8px; padding:4px 12px; font-size:12px;
                            color:#8888aa; font-family: DM Mono, monospace;'>
                    📡 {dossier['source']}
                </div>
                <div style='background:#1a1a35; border-radius:8px; padding:4px 12px; font-size:12px;
                            color:#8888aa; font-family: DM Mono, monospace;'>
                    🎯 {dossier['analysis']['priority']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Feed activité récente
st.markdown("### 🕒 Activité récente")

all_events = []
for d_id, dossier in st.session_state.dossiers.items():
    client = st.session_state.clients.get(dossier["client_id"], {})
    for event in dossier["timeline"]:
        all_events.append({
            "time": event["time"],
            "message": event["message"],
            "client": f"{client.get('nom','')} {client.get('prenom','')}"
        })

if not all_events:
    st.markdown("""
    <div style='color:#444466; font-size:14px; text-align:center; padding:20px;'>
        Aucune activité récente
    </div>
    """, unsafe_allow_html=True)
else:
    for ev in reversed(all_events[-8:]):
        st.markdown(f"""
        <div class='timeline-event'>
            <span style='color:#7755aa;'>{ev['time']}</span>
            &nbsp;—&nbsp;
            <span style='color:#9999cc;'>{ev['client']}</span>
            &nbsp;·&nbsp;
            {ev['message']}
        </div>
        """, unsafe_allow_html=True)
```

# =========================

# MODE CLIENT — WIZARD 3 ÉTAPES

# =========================

elif mode == “👤 Client”:

```
st.markdown("## 👤 Espace Client")

# Wizard progress
step = st.session_state.client_step
steps_labels = ["Vos coordonnées", "Votre situation", "Vos documents"]

progress_pct = (step - 1) / (len(steps_labels) - 1) if len(steps_labels) > 1 else 1.0

cols_steps = st.columns(len(steps_labels))
for i, label in enumerate(steps_labels, start=1):
    with cols_steps[i - 1]:
        if i < step:
            color = "#27ae60"
            icon = "✅"
        elif i == step:
            color = "#5599ee"
            icon = "🔵"
        else:
            color = "#333355"
            icon = "⬜"
        st.markdown(f"""
        <div style='text-align:center; padding:10px;'>
            <div style='font-size:20px;'>{icon}</div>
            <div style='font-size:12px; color:{color}; font-weight:600; margin-top:4px;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.progress(progress_pct)
st.markdown("<br>", unsafe_allow_html=True)

# ---- ÉTAPE 1 : Coordonnées ----
if step == 1:
    st.markdown("### 1️⃣ Vos coordonnées")

    nom = st.text_input("Nom *", value=st.session_state.client_form_data.get("nom", ""))
    prenom = st.text_input("Prénom *", value=st.session_state.client_form_data.get("prenom", ""))
    societe = st.text_input("Société (optionnel)", value=st.session_state.client_form_data.get("societe", ""))
    email = st.text_input("Email *", value=st.session_state.client_form_data.get("email", ""))
    tel = st.text_input("Téléphone *", value=st.session_state.client_form_data.get("tel", ""))

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Suivant →", key="step1_next"):
        if nom.strip() and prenom.strip() and email.strip():
            st.session_state.client_form_data.update({
                "nom": nom, "prenom": prenom,
                "societe": societe, "email": email, "tel": tel
            })
            st.session_state.client_step = 2
            st.rerun()
        else:
            st.error("⚠️ Veuillez remplir les champs obligatoires (Nom, Prénom, Email)")

# ---- ÉTAPE 2 : Situation ----
elif step == 2:
    st.markdown("### 2️⃣ Votre situation juridique")

    description = st.text_area(
        "Décrivez votre situation en détail *",
        value=st.session_state.client_form_data.get("description", ""),
        height=180,
        placeholder="Expliquez votre problème juridique, les faits importants, les dates clés..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← Retour", key="step2_back"):
            st.session_state.client_form_data["description"] = description
            st.session_state.client_step = 1
            st.rerun()
    with col_next:
        if st.button("Suivant →", key="step2_next"):
            if description.strip():
                st.session_state.client_form_data["description"] = description
                st.session_state.client_step = 3
                st.rerun()
            else:
                st.error("⚠️ Veuillez décrire votre situation")

# ---- ÉTAPE 3 : Documents + Envoi ----
elif step == 3:
    st.markdown("### 3️⃣ Vos documents")

    uploaded_files = st.file_uploader(
        "Ajoutez vos documents (contrats, courriers, emails...)",
        accept_multiple_files=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Récap
    fd = st.session_state.client_form_data
    st.markdown(f"""
    <div class='juri-card'>
        <div style='font-size:13px; color:#8888aa; margin-bottom:8px; text-transform:uppercase;
                    font-family: DM Mono, monospace; letter-spacing:1px;'>Récapitulatif</div>
        <div style='font-size:15px; color:#e0e0f5;'>👤 {fd.get('nom','')} {fd.get('prenom','')}</div>
        {"<div style='font-size:13px; color:#9999bb;'>🏢 " + fd.get('societe','') + "</div>" if fd.get('societe') else ""}
        <div style='font-size:13px; color:#9999bb;'>📧 {fd.get('email','')}</div>
        <div style='font-size:13px; color:#9999bb; margin-top:6px;'>📝 {fd.get('description','')[:80]}...</div>
    </div>
    """, unsafe_allow_html=True)

    col_back2, col_send = st.columns(2)
    with col_back2:
        if st.button("← Retour", key="step3_back"):
            st.session_state.client_step = 2
            st.rerun()
    with col_send:
        if st.button("📩 Envoyer la demande", key="step3_send"):
            fd = st.session_state.client_form_data
            client_id = create_client(
                fd.get("nom", ""),
                fd.get("prenom", ""),
                fd.get("societe", ""),
                fd.get("email", ""),
                fd.get("tel", "")
            )
            dossier_id = create_dossier(
                client_id,
                fd.get("description", ""),
                "PLATEFORME_CLIENT"
            )

            if uploaded_files:
                for f in uploaded_files:
                    st.session_state.dossiers[dossier_id]["files"].append(f.name)
                    add_event(dossier_id, f"📄 Fichier ajouté : {f.name}")

            # Confirmation
            st.success("✅ Votre demande a été transmise au cabinet.")

            st.markdown("""
            <div class='juri-card'>
                <div style='font-size:13px; color:#8888aa; margin-bottom:8px; text-transform:uppercase;
                            font-family: DM Mono, monospace; letter-spacing:1px;'>Analyse IA — Aperçu</div>
            """, unsafe_allow_html=True)
            analysis = st.session_state.dossiers[dossier_id]["analysis"]
            st.json(analysis)
            st.markdown("</div>", unsafe_allow_html=True)

            st.warning("⚠️ Ceci est une assistance IA. Validation par un avocat requise.")

            # Reset wizard
            st.session_state.client_step = 1
            st.session_state.client_form_data = {}

st.markdown("<hr style='border-color:#2a2a3a; margin:24px 0;'>", unsafe_allow_html=True)

# Bouton urgence visible en bas du mode client
st.markdown("""
<div style='background: linear-gradient(135deg,#2a0808,#3a1010); border:1px solid #8b2020;
            border-radius:14px; padding:16px 20px; text-align:center; margin-top:8px;'>
    <div style='color:#ff6666; font-weight:700; font-size:15px; margin-bottom:4px;'>
        🔴 Situation d'urgence ?
    </div>
    <div style='color:#aa4444; font-size:13px;'>Contactez immédiatement le cabinet</div>
</div>
""", unsafe_allow_html=True)
if st.button("🚨 Contacter le Cabinet en URGENCE", key="client_urgence"):
    st.toast("🚨 Le cabinet a été notifié de votre urgence", icon="🚨")
```

# =========================

# MODE AVOCAT

# =========================

elif mode == “⚖️ Avocat”:

```
st.markdown("## ⚖️ Dashboard Avocat")

if st.session_state.shadow_mode:
    st.markdown("""
    <div class='shadow-active-banner'>👻 Shadow Mode ACTIF — L'IA structure en arrière-plan</div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style='background:#1a1a28; border:1px solid #2a2a3a; border-radius:12px;
                padding:10px 18px; color:#555577; font-size:13px; margin-bottom:16px;'>
        Shadow Mode OFF
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.dossiers:
    st.markdown("""
    <div class='juri-card' style='text-align:center; color:#555577; padding:40px;'>
        <div style='font-size:40px; margin-bottom:10px;'>⚖️</div>
        <div style='font-size:16px;'>Aucun dossier en cours</div>
    </div>
    """, unsafe_allow_html=True)

for d_id, dossier in st.session_state.dossiers.items():

    client = st.session_state.clients.get(dossier["client_id"], {})
    urgence = dossier["analysis"]["urgence"]
    badge_html = urgence_badge(urgence)

    with st.expander(
        f"📁  {client.get('nom','')} {client.get('prenom','')}  —  {dossier['analysis']['type']}"
    ):

        # En-tête dossier
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;'>
            <div>
                <div style='font-size:18px; font-weight:700; color:#ffffff;'>
                    {client.get('nom','')} {client.get('prenom','')}
                </div>
                {"<div style='font-size:13px; color:#9999bb;'>🏢 " + client.get('societe','') + "</div>" if client.get('societe') else ""}
                <div style='font-size:13px; color:#7777aa;'>
                    📧 {client.get('email','')} &nbsp;·&nbsp; 📞 {client.get('tel','')}
                </div>
            </div>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- WORKFLOW ----
        st.markdown("**📊 Avancement du dossier**")

        total_steps = len(dossier["workflow_steps"])
        current_stage = dossier["workflow_stage"]
        progress_value = current_stage / total_steps
        st.progress(progress_value)

        workflow_cols = st.columns(total_steps)
        for index, (step_name, wcol) in enumerate(
            zip(dossier["workflow_steps"], workflow_cols), start=1
        ):
            with wcol:
                if index < current_stage:
                    color = "#27ae60"
                    icon = "✅"
                elif index == current_stage:
                    color = "#5599ee"
                    icon = "🔵"
                else:
                    color = "#333355"
                    icon = "⬜"
                st.markdown(f"""
                <div style='text-align:center; font-size:11px; color:{color}; font-weight:600;'>
                    {icon}<br>{step_name}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- PRIORITÉ + CONFIDENCE ----
        col_prio, col_conf = st.columns(2)
        with col_prio:
            st.markdown(f"""
            <div class='juri-card' style='text-align:center;'>
                <div style='font-size:20px; font-weight:700; color:#e67e22;'>
                    {dossier['analysis']['priority']}
                </div>
                <div style='font-size:11px; color:#8888aa; text-transform:uppercase;
                            font-family: DM Mono, monospace; margin-top:4px;'>Priorité dossier</div>
            </div>
            """, unsafe_allow_html=True)
        with col_conf:
            conf = dossier['analysis']['confidence']
            conf_color = "#27ae60" if conf >= 80 else "#e67e22" if conf >= 60 else "#e74c3c"
            st.markdown(f"""
            <div class='juri-card' style='text-align:center;'>
                <div style='font-size:28px; font-weight:700; color:{conf_color};'>
                    {conf}%
                </div>
                <div style='font-size:11px; color:#8888aa; text-transform:uppercase;
                            font-family: DM Mono, monospace; margin-top:4px;'>Confiance IA</div>
            </div>
            """, unsafe_allow_html=True)

        # ---- FLAGS ----
        st.markdown("**🚩 Alertes détectées**")
        for flag in dossier["analysis"]["flags"]:
            st.error(flag)

        # ---- DEADLINES ----
        st.markdown("**⏳ Deadlines**")
        for deadline in dossier["analysis"]["deadlines"]:
            st.warning(deadline)

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- RÉSUMÉ IA ----
        st.markdown("**📌 Résumé IA**")
        st.markdown(f"""
        <div class='juri-card'>
            <div style='color:#c0c0d8; font-size:14px; line-height:1.6;'>
                {dossier['analysis']['resume']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- RISQUES ----
        st.markdown("**⚠️ Risques identifiés**")
        for risque in dossier["analysis"]["risques"]:
            st.markdown(f"""
            <div style='background:#1e1020; border-left:3px solid #aa3355; border-radius:0 10px 10px 0;
                        padding:8px 14px; margin-bottom:6px; font-size:13px; color:#cc8899;'>
                ⚠️ {risque}
            </div>
            """, unsafe_allow_html=True)

        # ---- PIÈCES ----
        st.markdown("**📎 Pièces nécessaires**")
        for piece in dossier["analysis"]["pieces"]:
            st.markdown(f"""
            <div style='background:#101e20; border-left:3px solid #337755; border-radius:0 10px 10px 0;
                        padding:8px 14px; margin-bottom:6px; font-size:13px; color:#88ccaa;'>
                📄 {piece}
            </div>
            """, unsafe_allow_html=True)

        # ---- FICHIERS ----
        st.markdown("**📂 Fichiers attachés**")
        if dossier["files"]:
            for f in dossier["files"]:
                st.markdown(f"""
                <div style='background:#1a1a28; border:1px solid #2e2e45; border-radius:10px;
                            padding:8px 14px; margin-bottom:6px; font-size:13px; color:#9999bb;'>
                    📄 {f}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#444466; font-size:13px;'>Aucun fichier attaché</div>",
                        unsafe_allow_html=True)

        # ---- SHADOW MODE LOCAL ----
        dossier["shadow_local"] = st.toggle(
            "👻 Shadow Mode — ce dossier",
            value=dossier["shadow_local"],
            key="shadow_" + d_id
        )

        # ---- UPLOAD DOCUMENTS ----
        st.markdown("**⬆️ Ajouter un document**")
        uploaded = st.file_uploader(
            "Déposer un document",
            key=d_id,
            accept_multiple_files=True
        )
        if uploaded:
            for f in uploaded:
                dossier["files"].append(f.name)
                add_event(d_id, f"📄 Document uploadé : {f.name}")
                st.success(ai_analyse_document(f.name))

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- ACTIONS RECOMMANDÉES ----
        st.markdown("**🧠 Actions recommandées**")
        for action in ["Contacter client", "Demander pièces manquantes", "Préparer RDV"]:
            st.markdown(f"""
            <div style='background:#101828; border:1px solid #1a3050; border-radius:10px;
                        padding:8px 14px; margin-bottom:6px; font-size:13px; color:#6699cc;'>
                → {action}
            </div>
            """, unsafe_allow_html=True)

        # ---- CHECKLIST ----
        st.markdown("**📋 Checklist dossier**")
        for i, task in enumerate(dossier["tasks"]):
            checked = st.checkbox(
                task["label"],
                value=task["done"],
                key=f"{d_id}_task_{i}"
            )
            if checked != task["done"] and checked:
                add_event(d_id, f"✅ Action terminée : {task['label']}")
            dossier["tasks"][i]["done"] = checked

        # Ajout manuel action
        new_task = st.text_input("➕ Ajouter une action", key=f"new_task_{d_id}")
        if st.button("Ajouter action", key=f"add_task_{d_id}"):
            if new_task.strip():
                dossier["tasks"].append({"label": new_task, "done": False})
                add_event(d_id, f"📝 Nouvelle action ajoutée : {new_task}")
                st.success("✅ Action ajoutée")

        # Auto-update workflow — logique correcte avec elif
        completed_tasks = sum(1 for task in dossier["tasks"] if task["done"])
        if completed_tasks >= 5:
            dossier["workflow_stage"] = 6
        elif completed_tasks >= 4:
            dossier["workflow_stage"] = 5
        elif completed_tasks >= 3:
            dossier["workflow_stage"] = 4
        elif completed_tasks >= 2:
            dossier["workflow_stage"] = 3
        elif completed_tasks >= 1:
            dossier["workflow_stage"] = 2
        else:
            dossier["workflow_stage"] = 1

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- COMMUNICATION CLIENT ----
        st.markdown("**📨 Communication client**")

        email_type = st.selectbox(
            "Type de communication",
            [
                "Demande de pièces",
                "Relance client",
                "Confirmation rendez-vous",
                "Synthèse dossier"
            ],
            key=f"email_type_{d_id}"
        )

        col_gen, col_prog = st.columns(2)

        with col_gen:
            if st.button("🧠 Générer email", key=f"generate_email_{d_id}"):
                generated_email = f"""Bonjour {client.get('prenom','')},
```

Suite à l’analyse de votre dossier concernant :
{dossier[‘analysis’][‘type’]},

Nous revenons vers vous concernant :
{email_type.lower()}.

Merci de transmettre les éléments nécessaires dans les meilleurs délais.

Cordialement,
Cabinet Juridique”””
# Stockage en session state pour éviter le bug de reset
st.session_state.email_drafts[d_id] = generated_email
add_event(d_id, f”📨 Brouillon email généré : {email_type}”)

```
        with col_prog:
            if st.button("📅 Programmer email", key=f"schedule_email_{d_id}"):
                add_event(d_id, "📅 Email programmé par avocat")
                st.success("📅 Email programmé (simulation MVP)")

        # Affichage du brouillon depuis session state — pas de bug de reset
        if d_id in st.session_state.email_drafts:
            st.text_area(
                "✉️ Brouillon email",
                value=st.session_state.email_drafts[d_id],
                height=220,
                key=f"email_content_{d_id}"
            )

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- TIMELINE ----
        st.markdown("**🕒 Timeline dossier**")
        for event in reversed(dossier["timeline"]):
            st.markdown(f"""
            <div class='timeline-event'>
                <span style='color:#7755aa;'>{event['time']}</span>
                &nbsp;—&nbsp;
                {event['message']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

        # ---- ACTIONS RAPIDES ----
        st.markdown("**⚡ Actions rapides**")

        col_call, col_urg = st.columns(2)

        with col_call:
            if st.button("📞 Appeler client", key="call_" + d_id):
                add_event(d_id, "📞 Appel client lancé par avocat")
                st.toast(f"📞 Appel vers {client.get('prenom','')} {client.get('nom','')}", icon="📞")

        with col_urg:
            if st.button("🚨 URGENCE Cabinet", key="urg_" + d_id):
                add_event(d_id, "🚨 Appel urgence cabinet déclenché")
                st.toast("🚨 Cabinet notifié en urgence", icon="🚨")

        st.markdown(f"""
        <div style='background:#1a1a28; border:1px solid #2a2a3a; border-radius:10px;
                    padding:8px 14px; margin-top:8px; font-size:12px; color:#555577;
                    font-family: DM Mono, monospace;'>
            📡 Source : {dossier['source']}
        </div>
        """, unsafe_allow_html=True)
```

# =========================

# AGENT IA

# =========================

elif mode == “🤖 Agent IA”:

```
st.markdown("## 🤖 Agent JuriEngine")

st.markdown("""
<div class='juri-card'>
    <div style='font-size:13px; color:#8888aa; text-transform:uppercase;
                font-family: DM Mono, monospace; letter-spacing:1px; margin-bottom:8px;'>
        Assistant contextuel du cabinet
    </div>
    <div style='color:#c0c0d8; font-size:14px; line-height:1.6;'>
        Posez une question sur un dossier, demandez une note juridique,
        une stratégie ou un courrier. L'agent analyse et structure la réponse.
    </div>
</div>
""", unsafe_allow_html=True)

# Sélecteur de dossier contextuel
dossier_options = {"— Aucun dossier sélectionné —": None}
for d_id, dossier in st.session_state.dossiers.items():
    client = st.session_state.clients.get(dossier["client_id"], {})
    label = f"{client.get('nom','')} {client.get('prenom','')} — {dossier['analysis']['type']}"
    dossier_options[label] = d_id

selected_label = st.selectbox(
    "Contexte dossier (optionnel)",
    list(dossier_options.keys())
)
selected_d_id = dossier_options[selected_label]

question = st.text_area(
    "Votre question ou demande",
    height=120,
    placeholder="Ex: Rédige une note juridique sur les risques de ce dossier..."
)

col_q1, col_q2, col_q3 = st.columns(3)
with col_q1:
    if st.button("📝 Note juridique", key="agent_note"):
        st.session_state["agent_question"] = "Rédige une note juridique complète pour ce dossier"
with col_q2:
    if st.button("⚖️ Stratégie", key="agent_strat"):
        st.session_state["agent_question"] = "Quelle stratégie recommandes-tu pour ce dossier ?"
with col_q3:
    if st.button("📄 Courrier", key="agent_courrier"):
        st.session_state["agent_question"] = "Rédige un courrier formel pour ce dossier"

if st.button("🧠 Analyser", key="agent_analyse"):
    q = question or st.session_state.get("agent_question", "")
    if q.strip():
        st.markdown("""
        <div class='juri-card'>
            <div style='font-size:13px; color:#8888aa; text-transform:uppercase;
                        font-family: DM Mono, monospace; letter-spacing:1px; margin-bottom:12px;'>
                Analyse IA — Résultat
            </div>
        """, unsafe_allow_html=True)

        st.success("✅ Analyse IA simulée — Version MVP")

        st.markdown("""
        <div style='color:#c0c0d8; font-size:14px; line-height:1.8;'>
            <b style='color:#ffffff;'>Synthèse du dossier</b><br>
            → Situation analysée, risques identifiés, stratégie recommandée disponible<br><br>
            <b style='color:#ffffff;'>Risques principaux</b><br>
            → Délai de prescription à surveiller<br>
            → Pièces manquantes à demander en priorité<br><br>
            <b style='color:#ffffff;'>Stratégie recommandée</b><br>
            → Contact client sous 48h<br>
            → Constitution du dossier documentaire<br>
            → Mise en demeure si nécessaire<br><br>
            <b style='color:#ffffff;'>Points d'attention</b><br>
            → Vérification délais légaux obligatoire<br>
            → Validation avocat requise avant toute action
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if selected_d_id:
            add_event(selected_d_id, f"🤖 Agent IA consulté : {q[:40]}...")
    else:
        st.warning("⚠️ Veuillez saisir une question ou utiliser un raccourci")

st.markdown("<hr class='juri-divider'>", unsafe_allow_html=True)

st.warning("⚠️ Outil d'assistance uniquement — Validation avocat obligatoire avant toute action")
```

# =========================

# ARCHIVES

# =========================

elif mode == “🗂️ Archives”:

```
st.markdown("## 🗂️ Archives")

if not st.session_state.dossiers:
    st.markdown("""
    <div class='juri-card' style='text-align:center; color:#555577; padding:40px;'>
        <div style='font-size:40px; margin-bottom:10px;'>🗂️</div>
        <div style='font-size:16px;'>Aucun dossier archivé</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for d_id, dossier in st.session_state.dossiers.items():
        client = st.session_state.clients.get(dossier["client_id"], {})
        urgence = dossier["analysis"]["urgence"]
        badge_html = urgence_badge(urgence)

        st.markdown(f"""
        <div class='juri-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='font-size:15px; font-weight:700; color:#ffffff;'>
                        👤 {client.get('nom','')} {client.get('prenom','')}
                    </div>
                    {"<div style='font-size:12px; color:#9999bb;'>🏢 " + client.get('societe','') + "</div>" if client.get('societe') else ""}
                    <div style='font-size:13px; color:#7777aa; margin-top:4px;'>
                        📌 {dossier['analysis']['type']}
                    </div>
                    <div style='font-size:12px; color:#555577; margin-top:2px;
                                font-family: DM Mono, monospace;'>
                        📡 {dossier['source']}
                    </div>
                </div>
                {badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
```

# =========================

# MODE CLIENTS

# =========================

elif mode == “👥 Clients”:

```
st.markdown("## 👥 Clients confirmés")

if not st.session_state.clients:
    st.markdown("""
    <div class='juri-card' style='text-align:center; color:#555577; padding:40px;'>
        <div style='font-size:40px; margin-bottom:10px;'>👥</div>
        <div style='font-size:16px;'>Aucun client enregistré</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for client_id, client in st.session_state.clients.items():

        with st.expander(
            f"👤  {client['nom']} {client['prenom']}"
            + (f"  —  🏢 {client['societe']}" if client.get('societe') else "")
        ):
            # Fiche client
            st.markdown(f"""
            <div class='juri-card'>
                <div style='font-size:16px; font-weight:700; color:#ffffff; margin-bottom:10px;'>
                    👤 {client['nom']} {client['prenom']}
                </div>
                {"<div style='font-size:13px; color:#9999bb; margin-bottom:4px;'>🏢 " + client.get('societe','') + "</div>" if client.get('societe') else ""}
                <div style='font-size:13px; color:#7777aa;'>📞 {client['tel']}</div>
                <div style='font-size:13px; color:#7777aa;'>📧 {client['email']}</div>
                <div style='font-size:12px; color:#444466; margin-top:8px; font-family: DM Mono, monospace;'>
                    Depuis le {client['created_at'].strftime("%d/%m/%Y à %H:%M")}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**📁 Dossiers liés**")

            if not client.get("dossiers"):
                st.markdown("<div style='color:#444466; font-size:13px;'>Aucun dossier lié</div>",
                            unsafe_allow_html=True)
            else:
                for d_id in client.get("dossiers", []):
                    dossier = st.session_state.dossiers.get(d_id)
                    if dossier:
                        urgence = dossier["analysis"]["urgence"]
                        badge_html = urgence_badge(urgence)

                        st.markdown(f"""
                        <div class='juri-card' style='margin-bottom:8px;'>
                            <div style='display:flex; justify-content:space-between; align-items:center;'>
                                <div style='font-size:13px; color:#c0c0d8;'>
                                    📌 {dossier['analysis']['type']}
                                </div>
                                {badge_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button(
                            f"📂 Ouvrir ce dossier",
                            key="open_" + d_id
                        ):
                            st.session_state.selected_client_id = client_id
                            st.success(
                                f"✅ Dossier sélectionné — "
                                f"Rendez-vous dans l'onglet ⚖️ Avocat pour le consulter"
                            )
```
