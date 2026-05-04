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

    # 🔥 NEW BACKDOOR LOG
    c.execute("""
    CREATE TABLE IF NOT EXISTS urgent_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        description TEXT,
        status TEXT DEFAULT 'NEW'
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
    if "optimisation" in t or "payer moins" in t:
        score += 5

    score = min(score, 100)

    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"
    return score, level

# =========================
# TYPE DETECTION
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
# URGENCE LABEL
# =========================
def urgency_label(score):
    if score > 70:
        return "🔴 URGENT"
    if score > 40:
        return "🟠 IMPORTANT"
    return "🟢 NORMAL"

# =========================
# IA UNCERTAINTY DETECTION (NEW)
# =========================
def is_uncertain(text):
    return len(text.split()) < 8  # simple heuristic MVP

# =========================
# CHECKLIST
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
# COPILOT (simplifié stable)
# =========================
def copilot(text, score):

    dtype = detect_type(text)

    legal = (
        "Risque élevé" if score > 70 else
        "Risque modéré" if score > 40 else
        "Risque faible"
    )

    docs = ["Relevés bancaires", "Factures clients"]

    actions = [
        "Contacter client",
        "Collecter documents",
        "Analyser incohérences",
        "Préparer réponse fiscale"
    ]

    note = f"""
NOTE JURIDIQUE INTERNE

TYPE : {dtype}

FAITS :
{text}

QUALIFICATION :
{legal}

RISQUE :
{score}/100

⚠️ À VALIDER PAR AVOCAT
"""

    return legal, docs, actions, note, dtype

# =========================
# CLIENT VIEW (FIX + BACKDOOR)
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

        st.success("Votre dossier a été transmis au cabinet")

        dtype = detect_type(text)

        st.subheader("🧠 Synthèse de votre demande")

        st.info(f"""
👤 {name}

📌 Type : {dtype}

⚡ Urgence : {urgency_label(score)}
""")

        st.subheader("📄 Compréhension de votre demande")

        st.write(text)

        st.subheader("📎 Documents nécessaires")

        docs = copilot(text, score)[1]

        for d in docs:
            st.write("•", d)

        st.subheader("📞 Prochaines étapes")

        st.write("""
Un avocat va analyser votre dossier.
Vous serez contacté rapidement.
""")

    # =========================
    # 🚨 BACKDOOR HUMAN ESCALATION
    # =========================
    st.divider()
    st.subheader("🚨 Besoin d’un avocat immédiatement ?")

    st.warning("En cas d'urgence ou si votre situation est complexe, vous pouvez demander un rappel humain direct.")

    urgent = st.button("📞 Parler à un avocat maintenant")

    if urgent:

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        INSERT INTO urgent_requests (client_name, description)
        VALUES (?,?)
        """, (name, text))

        conn.commit()
        conn.close()

        st.success("Demande envoyée. Un avocat va vous recontacter rapidement.")

# =========================
# AVOCAT VIEW
# =========================
def lawyer_view():

    st.title("⚖️ OS Cabinet - Copilot Avocat")

    conn = get_conn()
    c = conn.cursor()

    dossiers = c.execute("SELECT * FROM dossiers").fetchall()

    for d in dossiers:

        legal, docs, actions, note, dtype = copilot(d[5], d[6])

        with st.expander(f"{d[1]} | {dtype} | Score {d[6]} ({d[7]})"):

            st.write("Nom:", d[1])
            st.write("Email:", d[2] or "N/A")
            st.write("Téléphone:", d[3] or "N/A")
            st.write("Société:", d[4] or "N/A")

            st.write("Description:", d[5])

            st.subheader("🧠 Analyse IA")
            st.write(legal)

            st.subheader("📎 Documents")
            for doc in docs:
                st.write("•", doc)

            st.subheader("🧭 Actions")
            for act in actions:
                st.write("•", act)

            st.subheader("📄 Note juridique")
            st.code(note)

    # =========================
    # URGENT REQUEST PANEL
    # =========================
    st.divider()
    st.subheader("🚨 Demandes urgentes clients")

    urgents = c.execute("SELECT * FROM urgent_requests WHERE status='NEW'").fetchall()

    for u in urgents:
        st.error(f"""
Client: {u[1]}
Demande: {u[2]}
""")

    conn.close()

# =========================
# ROUTING
# =========================
role = st.sidebar.selectbox("Mode utilisateur", ["Client", "Avocat"])

if role == "Client":
    client_view()
else:
    lawyer_view()
