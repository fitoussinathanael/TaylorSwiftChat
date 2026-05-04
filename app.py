import streamlit as st
import sqlite3
import os
from groq import Groq

# -----------------------
# CONFIG
# -----------------------
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine MVP", layout="wide")

# -----------------------
# IA CLIENT (GROQ)
# -----------------------
def analyze_with_ai(client_message):

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
Tu es un avocat fiscaliste senior dans un cabinet.

Analyse le message client suivant :

{client_message}

Retourne une analyse structurée :

1. Résumé du problème
2. Qualification juridique/fiscale
3. Risques identifiés
4. Pièces manquantes
5. Actions recommandées
"""

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "Tu es un avocat fiscaliste expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# -----------------------
# INIT DB
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

    conn.commit()
    conn.close()


# init
init_db()
seed_data()

# -----------------------
# DB CONNECTION
# -----------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------
# ROLE SYSTEM
# -----------------------
role = st.sidebar.selectbox(
    "Mode utilisateur",
    ["Client", "Avocat"]
)

# =====================================================
# 👤 CLIENT MODE (PORTAL SIMPLIFIÉ)
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique du Cabinet")

    st.write("""
Bonjour 👋  
Je suis votre assistant juridique.

Je vais vous aider à :
- comprendre votre situation
- analyser votre problème fiscal
- créer votre dossier
- préparer les documents nécessaires
""")

    st.divider()

    client_message = st.text_area(
        "Décrivez votre situation",
        placeholder="Ex : j'ai reçu un contrôle fiscal TVA..."
    )

    if client_message:

        if st.button("Analyser ma situation"):

            with st.spinner("Analyse juridique en cours..."):

                result = analyze_with_ai(client_message)

            st.success("Analyse terminée")

            st.write("### ⚖️ Analyse juridique")
            st.write(result)

# =====================================================
# ⚖️ AVOCAT MODE (BACKOFFICE COMPLET)
# =====================================================
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
