```python
import streamlit as st
from datetime import datetime
import uuid

# =========================
# CONFIG PAGE
# =========================

st.set_page_config(
    page_title="JuriEngine",
    page_icon="⚖️",
    layout="wide"
)

# =========================
# CSS GLOBAL — STYLE APP IPHONE
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fond général /
.stApp {
    background-color: #0f0f14;
    color: #f0f0f5;
}

/ Sidebar /
section[data-testid="stSidebar"] {
    background-color: #16161e;
    border-right: 1px solid #2a2a3a;
}

section[data-testid="stSidebar"] * {
    color: #d0d0e0 !important;
}

/ Titres /
h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    color: #ffffff;
}

/ Cards personnalisées */
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
# IA SIMULÉE (MVP)
# =========================

def ai_structurate(text):
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
        "confidence": 82
    }

def ai_analyse_document(file_name):
    return f"""Analyse du document : {file_name}

— Type détecté : PDF juridique
— Points clés : clauses contractuelles détectées
— Risques : à vérifier par avocat
— Synthèse : document ajouté au dossier"""

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

    else:
        for d_id, dossier in list(st.session_state.dossiers.items())[-5:]:

            client = st.session_state.clients.get(
                dossier["client_id"],
                {}
            )

            st.markdown(f"""
            <div class='juri-card'>
                <b>👤 {client.get('nom','')} {client.get('prenom','')}</b><br>
                📌 {dossier['analysis']['type']}
            </div>
            """, unsafe_allow_html=True)

# =========================
# MODE CLIENT
# =========================

elif mode == "👤 Client":

    st.markdown("## 👤 Espace Client")

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

    elif step == 2:

        description = st.text_area(
            "Décrivez votre situation"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Retour"):
                st.session_state.client_step = 1
                st.rerun()

        with col2:
            if st.button("Suivant →"):

                if description:

                    st.session_state.client_form_data[
                        "description"
                    ] = description

                    st.session_state.client_step = 3
                    st.rerun()

                else:
                    st.error("Veuillez décrire votre situation")

    elif step == 3:

        uploaded_files = st.file_uploader(
            "Ajoutez vos documents",
            accept_multiple_files=True
        )

        if st.button("📩 Envoyer la demande"):

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

            st.success("✅ Votre demande a été transmise au cabinet.")

            analysis = st.session_state.dossiers[dossier_id]["analysis"]

            st.json(analysis)

            st.session_state.client_step = 1
            st.session_state.client_form_data = {}

# =========================
# MODE AVOCAT
# =========================

elif mode == "⚖️ Avocat":

    st.markdown("## ⚖️ Dashboard Avocat")

    if not st.session_state.dossiers:
        st.info("Aucun dossier en cours")

    for d_id, dossier in list(st.session_state.dossiers.items()):

        client = st.session_state.clients.get(
            dossier["client_id"],
            {}
        )

        with st.expander(
            f"📁 {client.get('nom','')} {client.get('prenom','')}"
        ):

            st.markdown(f"""
            <div class='juri-card'>
                <b>{client.get('nom','')} {client.get('prenom','')}</b><br>
                📧 {client.get('email','')}<br>
                📞 {client.get('tel','')}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📌 Résumé IA")

            st.write(dossier["analysis"]["resume"])

            st.markdown("### ⚠️ Risques")

            for risque in dossier["analysis"]["risques"]:
                st.warning(risque)

            st.markdown("### 📎 Pièces")

            for piece in dossier["analysis"]["pieces"]:
                st.info(piece)

            st.markdown("### 📂 Documents")

            if dossier["files"]:
                for f in dossier["files"]:
                    st.write(f"📄 {f}")
            else:
                st.write("Aucun document")

            uploaded = st.file_uploader(
                "Ajouter document",
                key=d_id,
                accept_multiple_files=True
            )

            if uploaded:
                for f in uploaded:
                    dossier["files"].append(f.name)
                    st.success(ai_analyse_document(f.name))

            st.markdown("### 📋 Checklist")

            for i, task in enumerate(dossier["tasks"]):

                checked = st.checkbox(
                    task["label"],
                    value=task["done"],
                    key=f"{d_id}{i}"
                )

                dossier["tasks"][i]["done"] = checked

            st.markdown("### 📨 Communication")

            email_type = st.selectbox(
                "Type de communication",
                [
                    "Demande de pièces",
                    "Relance client",
                    "Confirmation rendez-vous"
                ],
                key=f"email{d_id}"
            )

            if st.button(
                "🧠 Générer email",
                key=f"generate_{d_id}"
            ):

                generated_email = f"""Bonjour {client.get('prenom','')},

Suite à l’analyse de votre dossier concernant :
{dossier['analysis']['type']},

Nous revenons vers vous concernant :
{email_type.lower()}.

Merci de transmettre les éléments nécessaires dans les meilleurs délais.

Cordialement,
Cabinet Juridique"""

                st.session_state.email_drafts[d_id] = generated_email

            if d_id in st.session_state.email_drafts:

                st.text_area(
                    "✉️ Brouillon email",
                    value=st.session_state.email_drafts[d_id],
                    height=220,
                    key=f"draft_{d_id}"
                )

# =========================
# AGENT IA
# =========================

elif mode == "🤖 Agent IA":

    st.markdown("## 🤖 Agent JuriEngine")

    question = st.text_area(
        "Votre question"
    )

    if st.button("🧠 Analyser"):

        if question:

            st.success("✅ Analyse IA simulée — MVP")

            st.markdown("""
            ### Synthèse
            - Situation analysée
            - Risques identifiés
            - Stratégie recommandée
            """)

        else:
            st.warning("Veuillez saisir une question")

# =========================
# ARCHIVES
# =========================

elif mode == "🗂️ Archives":

    st.markdown("## 🗂️ Archives")

    if not st.session_state.dossiers:
        st.info("Aucune archive")

    else:
        for d_id, dossier in st.session_state.dossiers.items():

            client = st.session_state.clients.get(
                dossier["client_id"],
                {}
            )

            st.markdown(f"""
            <div class='juri-card'>
                👤 {client.get('nom','')} {client.get('prenom','')}<br>
                📌 {dossier['analysis']['type']}
            </div>
            """, unsafe_allow_html=True)

# =========================
# CLIENTS
# =========================

elif mode == "👥 Clients":

    st.markdown("## 👥 Clients confirmés")

    if not st.session_state.clients:
        st.info("Aucun client enregistré")

    else:
        for client_id, client in st.session_state.clients.items():

            with st.expander(
                f"👤 {client['nom']} {client['prenom']}"
            ):

                st.markdown(f"""
                <div class='juri-card'>
                    📧 {client['email']}<br>
                    📞 {client['tel']}
                </div>
                """, unsafe_allow_html=True)

                if client.get("dossiers"):

                    for d_id in client["dossiers"]:

                        dossier = st.session_state.dossiers.get(d_id)

                        if dossier:
                            st.write(
                                f"📁 {dossier['analysis']['type']}"
