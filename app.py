import streamlit as st
import sqlite3

# -----------------------
# CONFIG
# -----------------------
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine MVP", layout="wide")

# -----------------------
# INIT DATABASE
# -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT,
        title TEXT,
        description TEXT,
        status TEXT,
        priority TEXT,
        fiscal_year TEXT,
        tax_type TEXT,
        client_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dossier_id INTEGER,
        title TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dossier_id INTEGER,
        name TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()

# -----------------------
# SEED DATA
# -----------------------
def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    cursor.execute("INSERT INTO users (name, role) VALUES ('Client A', 'client')")
    cursor.execute("INSERT INTO users (name, role) VALUES ('Client B', 'client')")
    cursor.execute("INSERT INTO users (name, role) VALUES ('Avocat Fiscaliste', 'lawyer')")

    cursor.execute("""
    INSERT INTO dossiers (reference, title, description, status, priority, fiscal_year, tax_type, client_id)
    VALUES ('FISC-001','Redressement TVA 2023','Contrôle fiscal e-commerce','en_cours','high','2023','TVA',1)
    """)

    cursor.execute("""
    INSERT INTO dossiers (reference, title, description, status, priority, fiscal_year, tax_type, client_id)
    VALUES ('FISC-002','IR revenus locatifs','Optimisation fiscale immobilier','en_cours','medium','2022','IR',2)
    """)

    cursor.execute("""
    INSERT INTO tasks (dossier_id, title, status)
    VALUES (1,'Demander pièces comptables','pending')
    """)

    cursor.execute("""
    INSERT INTO tasks (dossier_id, title, status)
    VALUES (2,'Vérifier déclaration revenus','pending')
    """)

    conn.commit()
    conn.close()

# init
init_db()
seed_data()

# -----------------------
# DB CONNECTION
# -----------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

conn = get_connection()
cursor = conn.cursor()

# -----------------------
# ROLE SYSTEM (IMPORTANT FIX)
# -----------------------
role = st.sidebar.selectbox(
    "Mode utilisateur",
    ["Client", "Avocat"]
)

# -----------------------
# CLIENT MODE (ISOLATED APP)
# -----------------------
if role == "Client":

    st.title("👤 Assistant Juridique Personnel")

    st.write("""
    Bonjour 👋  
    Je suis votre assistant du cabinet.

    Je vais vous aider à :
    - comprendre votre situation
    - constituer votre dossier
    - demander les bonnes pièces
    - suivre votre traitement
    """)

    st.divider()

    choice = st.radio(
        "Êtes-vous déjà client du cabinet ?",
        ["Oui, je suis client", "Non, premier contact"]
    )

    st.divider()

    if choice == "Oui, je suis client":

        st.success("Recherche de votre dossier dans le cabinet...")

        # simulation CRM
        dossiers = cursor.execute("""
            SELECT title, status, description
            FROM dossiers
        """).fetchall()

        st.write("### 📁 Vos dossiers")

        for d in dossiers:
            st.write("📄", d[0], "-", d[1])

        st.info("Un avocat va bientôt analyser votre situation.")

    else:

        st.info("Création d’un nouveau dossier en cours...")

        reason = st.text_area("Expliquez votre situation")

        if reason:
            st.write("### 🧠 Analyse automatique de votre demande")
            st.write("- structuration du besoin")
            st.write("- identification du type fiscal")
            st.write("- création dossier en cours")

            st.success("Votre dossier a été créé (simulation)")

# -----------------------
# LAWYER MODE (FULL BACKOFFICE)
# -----------------------
else:

    st.title("⚖️ JuriEngine - Backoffice Avocat")

    menu = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Dossiers", "Users", "Tasks"]
    )

    # -----------------------
    # DASHBOARD
    # -----------------------
    if menu == "Dashboard":

        st.subheader("📊 Vue globale du cabinet")

        dossiers = cursor.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dossiers", dossiers)
        col2.metric("Users", users)
        col3.metric("Tasks", tasks)

    # -----------------------
    # DOSSIERS
    # -----------------------
    elif menu == "Dossiers":

        st.subheader("📁 Dossiers fiscaux")

        rows = cursor.execute("""
            SELECT id, reference, title, description, status, priority, tax_type, fiscal_year
            FROM dossiers
        """).fetchall()

        for r in rows:

            with st.expander(f"{r[2]} | {r[4]}"):

                st.write("Reference:", r[1])
                st.write("Title:", r[2])
                st.write("Description:", r[3])
                st.write("Status:", r[4])
                st.write("Priority:", r[5])
                st.write("Tax type:", r[6])
                st.write("Fiscal year:", r[7])

                st.divider()

                if st.button(f"Analyser dossier {r[0]}", key=f"ai_{r[0]}"):

                    st.info("Analyse juridique en cours...")

                    st.write("### ⚖️ Résumé juridique")
                    st.write("- structuration du dossier fiscal")
                    st.write("- analyse des éléments déclarés")

                    st.write("### ⚠️ Risques fiscaux")
                    st.write("- incohérences potentielles")
                    st.write("- risque de redressement")

                    st.write("### 📌 Actions recommandées")
                    st.write("- relancer client")
                    st.write("- vérifier pièces")
                    st.write("- préparer réponse administration")

                    st.success("Analyse terminée")

    # -----------------------
    # USERS
    # -----------------------
    elif menu == "Users":

        st.subheader("👤 Utilisateurs")

        rows = cursor.execute("SELECT * FROM users").fetchall()
        st.write(rows)

    # -----------------------
    # TASKS
    # -----------------------
    elif menu == "Tasks":

        st.subheader("⚙️ Tasks / Actions")

        rows = cursor.execute("SELECT * FROM tasks").fetchall()
        st.write(rows)
