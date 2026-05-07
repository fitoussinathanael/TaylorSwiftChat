import streamlit as st
from datetime import datetime
import uuid

# =========================
# INIT SESSION STATE (CRM SIMULÉ)
# =========================

if "clients" not in st.session_state:
    st.session_state.clients = {}

if "dossiers" not in st.session_state:
    st.session_state.dossiers = {}

if "shadow_mode" not in st.session_state:
    st.session_state.shadow_mode = False

# =========================
# AJOUT : CLIENT SELECTION UI STATE
# =========================

if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = None


# =========================
# IA SIMULÉE (MVP)
# =========================

def ai_structurate(text):
    return {
        "resume": f"Résumé structuré de la demande : {text[:120]}...",
        "type": "Droit du travail (détecté)",
        "urgence": "MEDIUM",
        "risques": ["Risque de litige", "Délai légal à vérifier"],
        "pieces": ["Contrat de travail", "Emails", "Courriers reçus"]
    }


def ai_analyse_document(file_name):
    return f"""
Analyse du document : {file_name}

- Type détecté : PDF juridique
- Points clés : clauses contractuelles détectées
- Risques : à vérifier par avocat
- Synthèse : document ajouté au dossier
"""


# =========================
# UTILITAIRES
# =========================

def create_client(nom, prenom, email, tel):
    client_id = str(uuid.uuid4())

    st.session_state.clients[client_id] = {
        "nom": nom,
        "prenom": prenom,
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

        # =========================
        # SHADOW MODE LOCAL
        # =========================

        "shadow_local": False,

        # =========================
        # WORKFLOW DOSSIER
        # =========================

        "workflow_stage": 1,

        "workflow_steps": [
            "Intake",
            "Analyse",
            "Pièces",
            "Stratégie",
            "Action",
            "Clôture"
        ],

        # =========================
        # CHECKLIST DOSSIER
        # =========================

        "tasks": [
            {
                "label": "Contacter client",
                "done": False
            },
            {
                "label": "Demander pièces manquantes",
                "done": False
            },
            {
                "label": "Analyser documents",
                "done": False
            },
            {
                "label": "Préparer rendez-vous",
                "done": False
            }
        ]
    }

    # =========================
    # LIEN CLIENT → DOSSIER
    # =========================

    if client_id in st.session_state.clients:
        st.session_state.clients[client_id]["dossiers"].append(dossier_id)

    return dossier_id


# =========================
# UI GLOBAL
# =========================

st.set_page_config(
    page_title="JuriEngine MVP",
    layout="wide"
)

st.sidebar.title("⚖️ JuriEngine")

mode = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Client",
        "⚖️ Avocat",
        "🤖 Agent IA",
        "🗂️ Archives",
        "👥 Clients"
    ]
)

st.sidebar.markdown("---")

# =========================
# SHADOW MODE GLOBAL
# =========================

st.session_state.shadow_mode = st.sidebar.toggle(
    "👻 Shadow Mode",
    value=st.session_state.shadow_mode
)

if st.session_state.shadow_mode:
    st.sidebar.success("Shadow Mode ACTIVÉ")
else:
    st.sidebar.info("Shadow Mode OFF")


# =========================
# DASHBOARD
# =========================

if mode == "🏠 Dashboard":

    st.title("🏠 Dashboard JuriEngine")

    col1, col2, col3 = st.columns(3)

    col1.metric("Clients", len(st.session_state.clients))
    col2.metric("Dossiers", len(st.session_state.dossiers))
    col3.metric(
        "Shadow Mode",
        "ON" if st.session_state.shadow_mode else "OFF"
    )

    st.markdown("---")

    st.subheader("📌 Dossiers récents")

    for d_id, dossier in list(st.session_state.dossiers.items())[-5:]:

        client = st.session_state.clients.get(
            dossier["client_id"],
            {}
        )

        st.info(f"""
        👤 {client.get('nom','')} {client.get('prenom','')}  
        📌 {dossier['analysis']['type']}  
        🚨 Urgence : {dossier['analysis']['urgence']}  
        📡 Source : {dossier['source']}  
        """)


# =========================
# MODE CLIENT
# =========================

elif mode == "👤 Client":

    st.title("👤 Espace Client")

    st.subheader("1. Informations client")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("Email")
    tel = st.text_input("Téléphone")

    st.subheader("2. Votre demande")

    description = st.text_area(
        "Décrivez votre situation"
    )

    uploaded_files = st.file_uploader(
        "Documents",
        accept_multiple_files=True
    )

    if st.button("📩 Envoyer la demande"):

        client_id = create_client(
            nom,
            prenom,
            email,
            tel
        )

        dossier_id = create_dossier(
            client_id,
            description,
            "PLATEFORME_CLIENT"
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.dossiers[dossier_id]["files"].append(
                    f.name
                )

        st.success(
            "Votre demande a été transmise au cabinet."
        )

        st.info("🧠 Analyse IA")

        st.json(
            st.session_state.dossiers[dossier_id]["analysis"]
        )

        st.warning(
            "⚠️ Ceci est une assistance IA. Validation par un avocat requise."
        )

    st.markdown("---")

    st.error(
        "🔴 URGENCE : Contacter le cabinet immédiatement"
    )


# =========================
# MODE AVOCAT
# =========================

elif mode == "⚖️ Avocat":

    st.title("⚖️ Dashboard Avocat")

    st.subheader(
        "👻 Shadow Mode: " +
        (
            "ON"
            if st.session_state.shadow_mode
            else "OFF"
        )
    )

    for d_id, dossier in st.session_state.dossiers.items():

        client = st.session_state.clients.get(
            dossier["client_id"],
            {}
        )

        with st.expander(
            f"📁 {client.get('nom','')} - {dossier['analysis']['urgence']}"
        ):

            # =========================
            # BARRE AVANCEMENT DOSSIER
            # =========================

            st.write("### 📊 Avancement du dossier")

            total_steps = len(
                dossier["workflow_steps"]
            )

            current_stage = dossier["workflow_stage"]

            progress_value = current_stage / total_steps

            st.progress(progress_value)

            workflow_display = ""

            for index, step in enumerate(
                dossier["workflow_steps"],
                start=1
            ):

                if index < current_stage:
                    workflow_display += f"✅ {step} → "

                elif index == current_stage:
                    workflow_display += f"🟡 {step} → "

                else:
                    workflow_display += f"⬜ {step} → "

            st.write(workflow_display[:-2])

            st.markdown("---")

            # =========================
            # RÉSUMÉ IA
            # =========================

            st.write("### 📌 Résumé IA")
            st.write(dossier["analysis"]["resume"])

            # =========================
            # PIÈCES
            # =========================

            st.write("### 📎 Pièces nécessaires")
            st.write(dossier["analysis"]["pieces"])

            st.write("### 📂 Fichiers")

            if dossier["files"]:

                for f in dossier["files"]:
                    st.write("📄", f)

            else:
                st.write("Aucun fichier")

            # =========================
            # SHADOW LOCAL
            # =========================

            dossier["shadow_local"] = st.toggle(
                "👻 Shadow Mode dossier",
                value=dossier["shadow_local"],
                key="shadow_" + d_id
            )

            # =========================
            # UPLOAD DOCUMENTS
            # =========================

            uploaded = st.file_uploader(
                "Ajouter un document",
                key=d_id,
                accept_multiple_files=True
            )

            if uploaded:

                for f in uploaded:

                    dossier["files"].append(f.name)

                    st.success(
                        ai_analyse_document(f.name)
                    )

            st.markdown("---")

            # =========================
            # ACTIONS RECOMMANDÉES
            # =========================

            st.write("### 🧠 Actions recommandées")

            st.write("- Contacter client")
            st.write("- Demander pièces manquantes")
            st.write("- Préparer RDV")

            # =========================
            # CHECKLIST DOSSIER
            # =========================

            st.write("### 📋 Checklist dossier")

            for i, task in enumerate(dossier["tasks"]):

                checked = st.checkbox(
                    task["label"],
                    value=task["done"],
                    key=f"{d_id}_task_{i}"
                )

                dossier["tasks"][i]["done"] = checked

            # =========================
            # AJOUT MANUEL ACTION
            # =========================

            new_task = st.text_input(
                "➕ Ajouter une action",
                key=f"new_task_{d_id}"
            )

            if st.button(
                "Ajouter action",
                key=f"add_task_{d_id}"
            ):

                if new_task.strip():

                    dossier["tasks"].append({
                        "label": new_task,
                        "done": False
                    })

                    st.success("Action ajoutée")

            # =========================
            # AUTO UPDATE WORKFLOW
            # =========================

            completed_tasks = sum(
                1
                for task in dossier["tasks"]
                if task["done"]
            )

            if completed_tasks >= 1:
                dossier["workflow_stage"] = 2

            if completed_tasks >= 2:
                dossier["workflow_stage"] = 3

            if completed_tasks >= 3:
                dossier["workflow_stage"] = 4

            if completed_tasks >= 4:
                dossier["workflow_stage"] = 5

            if completed_tasks >= 5:
                dossier["workflow_stage"] = 6

            st.markdown("---")

            # =========================
            # ACTION RAPIDE
            # =========================

            st.button(
                "📞 Appeler client",
                key="call_" + d_id
            )

            st.info(
                f"📡 Source dossier : {dossier['source']}"
            )


# =========================
# AGENT IA
# =========================

elif mode == "🤖 Agent IA":

    st.title("🤖 Agent JuriEngine")

    st.write(
        "Assistant contextuel du cabinet"
    )

    question = st.text_area(
        "Pose une question sur un dossier"
    )

    if st.button("Analyser"):

        st.success("Analyse IA simulée")

        st.write("""
        - Synthèse du dossier
        - Risques principaux
        - Stratégie recommandée
        - Points d’attention
        """)

    st.warning(
        "⚠️ Outil d’assistance uniquement, validation avocat obligatoire"
    )


# =========================
# ARCHIVES
# =========================

elif mode == "🗂️ Archives":

    st.title("🗂️ Archives")

    for d_id, dossier in st.session_state.dossiers.items():

        client = st.session_state.clients.get(
            dossier["client_id"],
            {}
        )

        st.write(f"""
        ---
        👤 {client.get('nom','')}
        📌 {dossier['analysis']['type']}
        🚨 {dossier['analysis']['urgence']}
        📡 {dossier['source']}
        """)


# =========================
# MODE CLIENTS
# =========================

elif mode == "👥 Clients":

    st.title("👥 Clients confirmés")

    for client_id, client in st.session_state.clients.items():

        with st.expander(
            f"👤 {client['nom']} {client['prenom']}"
        ):

            st.write("📞", client["tel"])
            st.write("📧", client["email"])

            st.write("### 📁 Dossiers liés")

            for d_id in client.get("dossiers", []):

                dossier = st.session_state.dossiers.get(d_id)

                if dossier:

                    if st.button(
                        f"📂 Ouvrir dossier {dossier['analysis']['type']}",
                        key="open_" + d_id
                    ):

                        st.session_state.selected_client_id = client_id

                        st.success(
                            "Dossier sélectionné (navigation future possible)"
                        )
