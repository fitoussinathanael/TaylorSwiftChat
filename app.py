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

⚠️ À valider par avocat avant action
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

            # ------------------------
            # CLIENT INFO
            # ------------------------
            st.subheader("👤 Client")
            st.write("Nom:", d[1])
            st.write("Email:", d[2] or "N/A")
            st.write("Téléphone:", d[3] or "N/A")
            st.write("Société:", d[4] or "N/A")

            # ------------------------
            # DESCRIPTION (FIX CRITIQUE)
            # ------------------------
            st.subheader("📄 Description")
            st.write(d[5])

            # ------------------------
            # IA COPILOT
            # ------------------------
            legal, docs, actions, note = copilot(d[5], d[6])

            st.subheader("🧠 Analyse IA")
            st.write(legal)

            # ------------------------
            # DOCUMENTS
            # ------------------------
            st.subheader("📎 Pièces requises")
            for doc in docs:
                st.write("•", doc)

            # ------------------------
            # ACTIONS
            # ------------------------
            st.subheader("🧭 Actions")
            for act in actions:
                st.write("•", act)

            # ------------------------
            # CHECKLIST WORKFLOW
            # ------------------------
            st.divider()
            st.subheader("🧭 Checklist dossier")

            init_checklist(conn, dossier_id)

            tasks = c.execute("""
            SELECT id, task, done FROM checklist WHERE dossier_id=?
            """, (dossier_id,)).fetchall()

            done_count = 0

            for t in tasks:

                checked = st.checkbox(
                    t[1],
                    value=bool(t[2]),
                    key=f"{dossier_id}_{t[0]}"
                )

                if checked and t[2] == 0:
                    c.execute("UPDATE checklist SET done=1 WHERE id=?", (t[0],))

                if not checked and t[2] == 1:
                    c.execute("UPDATE checklist SET done=0 WHERE id=?", (t[0],))

                if checked:
                    done_count += 1

            conn.commit()

            # ------------------------
            # PROGRESSION
            # ------------------------
            progress = int((done_count / len(tasks)) * 100)
            st.progress(progress)

            st.write(f"Progression dossier : {progress}%")

            # ------------------------
            # ALERTES
            # ------------------------
            if progress < 100:
                st.warning(f"⚠️ Dossier incomplet ({progress}%)")

            if progress == 100:
                st.success("Dossier complet - prêt archivage")

                if st.button(f"Archiver dossier {dossier_id}"):
                    c.execute("""
                    UPDATE dossiers SET status='ARCHIVED' WHERE id=?
                    """, (dossier_id,))

                    conn.commit()
                    st.success("Dossier archivé (simulation)")

            # ------------------------
            # NOTE INTERNE
            # ------------------------
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
