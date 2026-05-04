import streamlit as st
import sqlite3

st.set_page_config(page_title="JuriEngine MVP", layout="wide")

st.title("⚖️ JuriEngine MVP - Fiscal Law")

# Connexion DB (adapte si besoin)
def get_connection():
    conn = sqlite3.connect("database.db")
    return conn

# -----------------------
# SIDEBAR NAVIGATION
# -----------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Dossiers", "Users", "Tasks"]
)

conn = get_connection()
cursor = conn.cursor()

# -----------------------
# DASHBOARD
# -----------------------
if menu == "Dashboard":
    st.subheader("📊 Vue globale du système")

    try:
        dossiers = cursor.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dossiers", dossiers)
        col2.metric("Users", users)
        col3.metric("Tasks", tasks)

    except Exception as e:
        st.warning(f"DB not fully connected yet: {e}")

# -----------------------
# DOSSIERS
# -----------------------
elif menu == "Dossiers":
    st.subheader("📁 Dossiers fiscaux")

    try:
        rows = cursor.execute("SELECT id, title, status, priority, tax_type FROM dossiers").fetchall()

        for r in rows:
            st.write({
                "id": r[0],
                "title": r[1],
                "status": r[2],
                "priority": r[3],
                "tax_type": r[4]
            })

    except Exception as e:
        st.error(f"Erreur dossiers: {e}")

# -----------------------
# USERS
# -----------------------
elif menu == "Users":
    st.subheader("👤 Utilisateurs")

    try:
        rows = cursor.execute("SELECT * FROM users").fetchall()
        st.write(rows)

    except Exception as e:
        st.error(f"Erreur users: {e}")

# -----------------------
# TASKS
# -----------------------
elif menu == "Tasks":
    st.subheader("⚙️ Tasks / Actions")

    try:
        rows = cursor.execute("SELECT * FROM tasks").fetchall()
        st.write(rows)

    except Exception as e:
        st.error(f"Erreur tasks: {e}")
