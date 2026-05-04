import streamlit as st
import sqlite3

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"
st.set_page_config(page_title="JuriEngine V15 OS Cabinet", layout="wide")

# =========================
# DB
# =========================
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        email TEXT,
        phone TEXT,
        company TEXT,
        description TEXT,
        score INTEGER,
        level TEXT,
        status TEXT DEFAULT 'INCOMING'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dossier_id INTEGER,
        task TEXT,
        done INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# RISK ENGINE
# =========================
def compute_risk(text):
    t = text.lower()
    score = 0

    if "contrôle fiscal" in t:
        score += 30
    if "incohérence" in t:
        score += 25
    if "compte personnel" in t:
        score += 20
    if "pas déclaré" in t:
        score += 30
    if "justificatif" in t:
        score += 10

    # 🔥 IMPORTANT: optimisation fiscale = pas risque mais complexité stratégique
    if "optimisation" in t or "payer moins" in t:
        score += 5

    score = min(score, 100)

    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"
    return score, level

# =========================
# TYPE DE DOSSIER (NEW PATCH)
# =========================
def detect_type(text):
    t = text.lower()

    if "optimisation" in t or "montage" in t:
        return "CONSEIL FISCAL STRATÉGIQUE"

    if "contrôle fiscal" in t or "redressement" in t:
        return "CONTENTIEUX FISCAL"

    if "justificatif" in t:
        return "ADMINISTRATIF / CONFORMITÉ"

    return "FISCAL GÉNÉRAL"

# =========================
# COPILOT AVOCAT (AMÉLIORÉ)
# =========================
def copilot(text, score):

    t = text.lower()
    dtype = detect_type(text)

    # =====================
    # CAS 1: STRATÉGIE
    # =====================
    if dtype == "CONSEIL FISCAL STRATÉGIQUE":

        legal = "Dossier de conseil en optimisation fiscale légale (non contentieux)."

        docs = [
            "Structure juridique de l’activité",
            "Bilan comptable détaillé",
            "Flux revenus / charges",
            "Organisation société (si existante)"
        ]

        actions = [
            "Analyse structure fiscale",
            "Identifier leviers d’optimisation légale",
            "Étude régime fiscal optimal",
            "Rendez-vous conseil client"
        ]

        note = f"""
NOTE INTERNE CABINET

TYPE : {dtype}

Score : {score}/100

Analyse :
Dossier stratégique de structuration fiscale.

Attention :
Ne pas traiter comme un contentieux.

Objectif :
Optimisation légale et structuration juridique.

⚠️ À VALIDER PAR AVOCAT FISCALISTE
"""

        return legal, docs, actions, note, dtype

    # =====================
    # CAS 2: CLASSIQUE
    # =====================
    legal = (
        "Risque élevé" if score > 70 else
        "Risque modéré" if score > 40 else
        "Risque faible"
    )

    docs = ["Relevés bancaires", "Factures clients"]

    if "compte personnel" in t:
        docs.append("Séparation compte pro/perso")

    actions = [
        "Contacter client",
        "Collecter documents",
        "Analyser incohérences",
        "Préparer réponse fiscale"
    ]

    note = f"""
NOTE INTERNE CABINET

TYPE : {dtype}

Score: {score}/100

{legal}

⚠️ À valider par avocat avant action
"""

    return legal, docs, actions, note, dtype

# =========================
# CHECKLIST ENGINE
# =========================
def init_checklist(conn, dossier_id):
    c = conn.cursor()

    existing = c.execute(
        "SELECT COUNT(*) FROM checklist WHERE dossier_id=?",
        (dossier_id,)
    ).fetchone()[0]

    if existing == 0:
        tasks = [
            "Contacter le client",
            "Collecter relevés bancaires",
            "Collecter factures clients",
            "Vérifier cohérence fiscale",
            "Préparer réponse administration"
        ]

        for t in tasks:
            c.execute(
                "INSERT INTO checklist (dossier_id, task, done) VALUES (?,?,0)",
                (dossier_id, t)
            )

# =========================
# CLIENT UX (AMÉLIORÉ)
# =========================
def client_view():

    st.title("👤 Assistant Juridique du Cabinet")

    name = st.text_input("Nom complet")
    email = st.text_input("Email")
    phone = st.text_input("Téléphone")
    company = st.text_input("Société")
    text = st.text_area("Décrivez votre situation")

    if name and text and st.button("Envoyer au cabinet"):

        score, level = compute_risk(text)

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        INSERT INTO dossiers
        (client_name, email, phone, company, description, score, level, status)
        VALUES (?,?,?,?,?,?,?,?)
        """, (name, email, phone, company, text, score, level, "INCOMING"))

        conn.commit()
        conn.close()

        dtype = detect_type(text)

        st.success("Votre dossier a été transmis au cabinet")

        # =========================
        # UX STRUCTURÉE CLIENT
        # =========================
        st.subheader("🧠 Synthèse de votre demande")

        st.info(f"""
👤 {name}

📌 Type de demande :
{dtype}

📄 Votre situation :
{text}
""")

        st.subheader("📌 Prise en charge")

        st.write("""
Votre dossier est en cours d’analyse par un avocat fiscaliste.

Étapes :
- analyse juridique
- vérification des documents
- préparation de la réponse adaptée
""")

        st.subheader("📎 Documents à préparer")

        docs = [
            "Relevés bancaires",
            "Factures clients",
            "Justificatifs fiscaux",
            "Contrats éventuels"
        ]

        for d in docs:
            st.write("•", d)

        st.subheader("📞 Suivi")

        st.info("Un avocat vous contactera si nécessaire.")

# =========================
# AVOCAT VIEW
# =========================
def lawyer_view():

    st.title("⚖️ OS Cabinet - Copilot Avocat")

    conn = get_conn()
    c = conn.cursor()

    dossiers = c.execute("SELECT * FROM dossiers").fetchall()

    for d in dossiers:

        dossier_id = d[0]

        legal, docs, actions, note, dtype = copilot(d[5], d[6])

        with st.expander(f"{d[1]} | {dtype} | Score {d[6]} ({d[7]})"):

            st.subheader("👤 Client")
            st.write("Nom:", d[1])
            st.write("Email:", d[2] or "N/A")
            st.write("Téléphone:", d[3] or "N/A")
            st.write("Société:", d[4] or "N/A")

            st.subheader("📄 Description")
            st.write(d[5])

            st.subheader("🧠 Analyse IA")
            st.write(legal)

            st.subheader("📎 Pièces requises")
            for doc in docs:
                st.write("•", doc)

            st.subheader("🧭 Actions")
            for act in actions:
                st.write("•", act)

            st.subheader("📄 Note interne")
            st.code(note)

            st.warning("⚠️ À valider par un avocat avant action")

    conn.close()

# =========================
# ROUTING
# =========================
role = st.sidebar.selectbox("Mode utilisateur", ["Client", "Avocat"])

if role == "Client":
    client_view()
else:
    lawyer_view()
