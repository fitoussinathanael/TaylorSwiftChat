import streamlit as st
from datetime import datetime
import uuid
import sqlite3

# =========================
# CONFIG PAGE
# =========================

st.set_page_config(
    page_title="JuriEngine",
    page_icon="⚖️",
    layout="wide"
)

# =========================
# DATABASE SQLITE
# =========================

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS legal_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    content TEXT
)
""")

conn.commit()

# =========================
# FONCTIONS DATABASE
# =========================

def get_legal_knowledge():

    cursor.execute("""
    SELECT category, title, content
    FROM legal_knowledge
    """)

    rows = cursor.fetchall()

    if not rows:
        return "Aucune donnée juridique disponible."

    text = ""

    for row in rows:
        text += f"""
Catégorie : {row[0]}
Titre : {row[1]}
Contenu : {row[2]}

"""

    return text

# =========================
# IA SIMULÉE + SQLITE
# =========================

def ai_structurate(text):

    legal_context = get_legal_knowledge()

    return {
        "resume": f"Résumé structuré de la demande : {text[:120]}...",
        "type": "Droit du travail (détecté)",
        "urgence": "MEDIUM",
        "priority": "🟠 PRIORITÉ MOYENNE",
        "risques": [
            "Risque de litige",
            "Délai légal à vérifier"
        ],
        "pieces": [
            "Contrat de travail",
            "Emails",
            "Courriers reçus"
        ],
        "deadlines": [
            "Prescription potentielle dans 12 jours",
            "Réponse employeur attendue sous 5 jours"
        ],
        "flags": [
            "⚠️ Pièces manquantes",
            "🚨 Vérifier délai légal"
        ],
        "confidence": 82,
        "knowledge_used": legal_context[:500]
    }

def ai_analyse_document(file_name):
    return f"""Analyse du document : {file_name}

— Type détecté : PDF juridique
— Points clés : clauses contractuelles détectées
— Risques : à vérifier par avocat
— Synthèse : document ajouté au dossier"""

def ai_agent_response(question):

    legal_context = get_legal_knowledge()

    return f"""
Analyse juridique simulée basée sur la base locale SQLite.

Question :
{question}

Connaissances disponibles :
{legal_context[:1500]}

⚠️ Réponse simulée pour tests MVP.
"""

# =========================
# CSS GLOBAL — STYLE APP IPHONE
# =========================

st.markdown("""
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

.juri-divider {
    border: none;
    border-top: 1px solid #2a2a3a;
    margin: 20px 0;
}

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

.stTextInput input,
.stTextArea textarea,
.stSelectbox select {
    background-color: #1e1e2e !important;
    border: 1px solid #3a3a55 !important;
    border-radius: 12px !important;
    color: #f0f0f5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #5555cc, #8844ee);
    border-radius: 10px;
}

.streamlit-expanderHeader {
    background: #1e1e2e !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

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

[data-testid="stMetric"] {
    background: #1e1e2e;
    border-radius: 16px;
    padding: 16px;
    border: 1px solid #2e2e45;
}

/* Bouton urgence */
div.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #8b0000, #cc0000) !important;
    border: 1px solid #ff4444 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# INIT SESSION STATE
# =========================

if "clients" not in st.session_state:
    st.session_state.clients = {}

if "dossiers" not in st.session_state:
    st.session_state.dossiers = {}

if "shadow_mode" not in st.session_state:
    st.session_state.shadow_mode = False

if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = None

if "client_step" not in st.session_state:
    st.session_state.client_step = 1

if "client_form_data" not in st.session_state:
    st.session_state.client_form_data = {}

if "email_drafts" not in st.session_state:
    st.session_state.email_drafts = {}

# =========================
# UTILITAIRE TIMELINE
# =========================

def add_event(dossier_id, message):
    if dossier_id in st.session_state.dossiers:
        st.session_state.dossiers[dossier_id]["timeline"].append({
            "time": datetime.now().strftime("%H:%M"),
            "message": message
        })

# =========================
# UTILITAIRES CRÉATION
# =========================

def create_client(nom, prenom, societe, email, tel):
    client_id = str(uuid.uuid4())

    st.session_state.clients[client_id] = {
        "nom": nom,
        "prenom": prenom,
        "societe": societe,
        "email": email,
        "tel": tel,
        "created_at": datetime.now(),
        "dossiers": []
    }

    return client_id

def create_dossier(client_id, description, source):

    dossier_id = str(uuid.uuid4())

    analysis = ai_structurate(description)

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

# =========================
# HELPER : BADGE URGENCE
# =========================

def urgence_badge(level):
    if level == "HIGH":
        return '<span class="badge-high">🔴 URGENT</span>'
    elif level == "MEDIUM":
        return '<span class="badge-medium">🟠 MOYEN</span>'
    else:
        return '<span class="badge-low">🟢 BAS</span>'

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.markdown("""
    <div style='padding: 8px 0 20px 0;'>
        <div style='font-size: 26px; font-weight: 800; color: #ffffff;'>
            ⚖️ JuriEngine
        </div>
        <div style='font-size: 11px; color: #6666aa;'>
            Orchestration Intelligente
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    st.session_state.shadow_mode = st.toggle(
        "👻 Shadow Mode",
        value=st.session_state.shadow_mode
    )

# =========================
# DASHBOARD
# =========================

if mode == "🏠 Dashboard":

    st.markdown("## 🏠 Dashboard JuriEngine")

    urgent_count = sum(
        1 for d in st.session_state.dossiers.values()
        if d["analysis"]["urgence"] == "HIGH"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Clients", len(st.session_state.clients))

    with col2:
        st.metric("Dossiers", len(st.session_state.dossiers))

    with col3:
        st.metric("Urgents", urgent_count)

    with col4:
        st.metric(
            "Shadow Mode",
            "ON" if st.session_state.shadow_mode else "OFF"
        )

    st.markdown("### 📌 Dossiers récents")

    if not st.session_state.dossiers:
        st.info("Aucun dossier pour le moment")

# =========================
# MODE CLIENT
# =========================

elif mode == "👤 Client":

    st.markdown("## 👤 Espace Client")

    st.markdown("### 🚨 Urgence")

    if st.button(
        "🚨 Parler à un membre du cabinet",
        type="secondary"
    ):
        st.error(
            "Un membre du cabinet va vous contacter dans les plus brefs délais."
        )

    step = st.session_state.client_step

    if step == 1:

        nom = st.text_input("Nom *")
        prenom = st.text_input("Prénom *")
        societe = st.text_input("Société")
        email = st.text_input("Email *")
        tel = st.text_input("Téléphone")

        if st.button("Suivant →"):

            if nom and prenom and email:

                st.session_state.client_form_data = {
                    "nom": nom,
                    "prenom": prenom,
                    "societe": societe,
                    "email": email,
                    "tel": tel
                }

                st.session_state.client_step = 2
                st.rerun()

            else:
                st.error("Veuillez remplir les champs obligatoires")
