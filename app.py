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
# IA CLIENT (CACHE GROQ CLIENT)
# -----------------------
@st.cache_resource
def get_ai_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_with_ai(client_message):
    client = get_ai_client()

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
# DB CONNECTION SAFE
# -----------------------
def get_conn():
    return sqlite3.connect(DB_PATH)

# -----------------------
# INIT DB
# -----------------------
def init_db():
    conn = get_conn()
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
    conn = get_conn()
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


# INIT
init_db()
seed_data()

# -----------------------
# ROLE SYSTEM
# -----------------------
role = st.sidebar.selectbox(
    "Mode utilisateur",
    ["Client", "Avocat"]
)

# =====================================================
# 👤 CLIENT MODE (CRM + IA)
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique du Cabinet")

    st.write("""
Bonjour 👋  
Je suis votre assistant juridique.

Je vais vous aider à :
- vérifier si vous êtes déjà dans notre système
- créer ou retrouver votre dossier
- analyser votre situation fiscale
""")

    st.divider()

    first_name = st.text_input("Prénom")
    last_name = st.text_input("Nom")

    client_message = st.text_area(
        "Décrivez votre situation",
        placeholder="Ex : j'ai reçu un contrôle fiscal TVA..."
    )

    if first_name and last_name and client_message:

        if st.button("Analyser ma situation"):

            full_name = f"{first_name} {last_name}"

            st.info(f"🔎 Recherche client : {full_name}")

            conn = get_conn()
            cursor = conn.cursor()

            # CRM SIMPLIFIÉ (MVP)
            client = cursor.execute(
                "SELECT id FROM users WHERE name LIKE ?",
                (f"%{first_name}%",)
            ).fetchone()

            if client:

                st.success("Client existant → dossier récupéré")

                dossier = cursor.execute("""
                    SELECT title, status, description
                    FROM dossiers
                    WHERE client_id = ?
                    LIMIT 1
                """, (client[0],)).fetchone()

                if dossier:
                    st.write("### 📁 Dossier existant")
                    st.write("Titre :", dossier[0])
                    st.write("Statut :", dossier[1])

            else:

                st.warning("Nouveau client → création dossier")

                cursor.execute("""
                    INSERT INTO dossiers (reference, title, description, status, priority, fiscal_year, tax_type, client_id)
                    VALUES ('AUTO','Nouveau dossier fiscal',?,'nouveau','medium','2026','GENERAL',1)
                """, (client_message,))

                conn.commit()

                st.success("📁 Dossier créé automatiquement")

            conn.close()

            # IA ANALYSE
            st.divider()

            with st.spinner("Analyse juridique en cours..."):

                result = analyze_with_ai(client_message)

            st.write("### ⚖️ Analyse juridique")
            st.write(result)


# =====================================================
# ⚖️ AVOCAT MODE (BACKOFFICE)
# =====================================================
else:

    st.title("⚖️ JuriEngine - Backoffice Avocat")

    menu = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Dossiers", "Users", "Tasks"]
    )

    conn = get_conn()
    cursor = conn.cursor()

    if menu == "Dashboard":

        st.subheader("📊 Vue globale du cabinet")

        dossiers = cursor.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dossiers", dossiers)
        col2.metric("Users", users)
        col3.metric("Tasks", tasks)

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

    elif menu == "Users":

        st.subheader("👤 Utilisateurs")
        st.write(cursor.execute("SELECT * FROM users").fetchall())

    elif menu == "Tasks":

        st.subheader("⚙️ Tasks / Actions")
        st.write(cursor.execute("SELECT * FROM tasks").fetchall())

    conn.close()
