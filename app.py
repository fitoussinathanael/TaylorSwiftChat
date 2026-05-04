import streamlit as st
import sqlite3

# -----------------------
# CONFIG
# -----------------------
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine MVP", layout="wide")

st.title("⚖️ JuriEngine MVP - Fiscal AI Cabinet")

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

    # USERS
    cursor.execute("INSERT INTO users (name, role) VALUES ('Client A', 'client')")
    cursor.execute("INSERT INTO users (name, role) VALUES ('Client B', 'client')")
    cursor.execute("INSERT INTO users (name, role) VALUES ('Avocat Fiscaliste', 'lawyer')")

    # DOSSIERS
    cursor.execute("""
    INSERT INTO dossiers (reference, title, description, status, priority, fiscal_year, tax_type, client_id)
    VALUES ('FISC-001','Redressement TVA 2023','Contrôle fiscal e-commerce','en_cours','high','2023','TVA',1)
    """)

    cursor.execute("""
    INSERT INTO dossiers (reference, title, description, status, priority, fiscal_year, tax_type, client_id)
    VALUES ('FISC-002','IR revenus locatifs','Optimisation fiscale immobilier','en_cours','medium','2022','IR',2)
    """)

    # TASKS
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

# run init
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
# SIDEBAR
# -----------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Dossiers", "Users", "Tasks"]
)

# -----------------------
# DASHBOARD
# -----------------------
if menu == "Dashboard":
    st.subheader("📊 Vue globale du cabinet")

    try:
        dossiers = cursor.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dossiers", dossiers)
        col2.metric("Users", users)
        col3.metric("Tasks", tasks)

    except Exception as e:
        st.error(f"DB error: {e}")

# -----------------------
# DOSSIERS INTERACTIFS (IMPORTANT)
# -----------------------
elif menu == "Dossiers":
    st.subheader("📁 Dossiers fiscaux interactifs")

    try:
        rows = cursor.execute("""
            SELECT id, reference, title, description, status, priority, tax_type, fiscal_year
            FROM dossiers
        """).fetchall()

        for r in rows:
            dossier_id = r[0]

            with st.expander(f"{r[2]} | {r[4]} | {r[5]}"):

                st.write("### 📄 Fiche dossier")
                st.write("ID:", r[0])
                st.write("Reference:", r[1])
                st.write("Title:", r[2])
                st.write("Description:", r[3])
                st.write("Status:", r[4])
                st.write("Priority:", r[5])
                st.write("Tax type:", r[6])
                st.write("Fiscal year:", r[7])

                st.divider()

                st.write("### 🧠 Analyse IA (simulation)")

                if st.button(f"Analyser dossier {dossier_id}", key=f"ai_{dossier_id}"):

                    st.info("Analyse IA en cours...")

                    st.write("#### ⚖️ Résumé juridique")
                    st.write("- Analyse du dossier fiscal en cours")
                    st.write("- Situation nécessitant vérification documentaire")

                    st.write("#### ⚠️ Risques fiscaux")
                    st.write("- incohérences potentielles dans déclarations")
                    st.write("- risque de redressement partiel")

                    st.write("#### 📌 Actions recommandées")
                    st.write("- collecter pièces justificatives")
                    st.write("- vérifier conformité fiscale")
                    st.write("- préparer réponse administration")

                    st.success("Analyse terminée (mode simulation)")

    except Exception as e:
        st.error(f"Dossiers error: {e}")

# -----------------------
# USERS
# -----------------------
elif menu == "Users":
    st.subheader("👤 Utilisateurs")

    try:
        rows = cursor.execute("SELECT * FROM users").fetchall()
        st.write(rows)

    except Exception as e:
        st.error(f"Users error: {e}")

# -----------------------
# TASKS
# -----------------------
elif menu == "Tasks":
    st.subheader("⚙️ Tasks / Actions")

    try:
        rows = cursor.execute("SELECT * FROM tasks").fetchall()
        st.write(rows)

    except Exception as e:
        st.error(f"Tasks error: {e}")
