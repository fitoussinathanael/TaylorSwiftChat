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

    # DOSSIERS
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

    # CHECKLIST WORKFLOW
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

    score = min(score, 100)
    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"

    return score, level

# =========================
# COPILOT AVOCAT
# =========================
def copilot(text, score):

    t = text.lower()

    if score > 70:
        legal = "Risque fiscal élevé nécessitant traitement prioritaire."
    elif score > 40:
        legal = "Risque modéré nécessitant analyse documentaire."
    else:
        legal = "Risque faible ou simple clarification."

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

Score: {score}/100

{legal}

⚠️ À valider par avocat
"""

    return legal, docs, actions, note

# =========================
# CHECKLIST ENGINE
# =========================
def init_checklist(conn, dossier_id):
    c = conn.cursor()

    existing = c.execute("""
    SELECT COUNT(*) FROM checklist WHERE dossier_id=?
    """, (dossier_id,)).fetchone()[0]

    if existing == 0:
        tasks = [
            "Contacter le client",
            "Collecter relevés bancaires",
            "Collecter factures clients",
            "Vérifier cohérence fiscale",
            "Préparer réponse administration"
        ]

        for t in tasks:
            c.execute("""
            INSERT INTO checklist (dossier_id, task, done)
            VALUES (?,?,0)
            """, (dossier_id, t))

# =========================
# CLIENT VIEW
# =========================
def client_view():

    st.title("👤 Assistant Juridique Cabinet")

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

        st.success("Votre dossier a été transmis au cabinet")

        st.info(f"""
Nous avons compris votre situation :

{name}, votre demande concerne un sujet fiscal nécessitant analyse.
Un avocat va prendre en charge votre dossier.
""")

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

        with st.expander(f"{d[1]} | Score {d[6]} ({d[7]})"):

            st.subheader("👤 Client")
            st.write(d[1], d[2], d[3], d[4])

            st.subheader("📄 Description")
            st
