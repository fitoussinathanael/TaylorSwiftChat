import streamlit as st
import sqlite3

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine V14 Copilot", layout="wide")

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
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# SCORING
# =========================
def compute_risk(text):
    t = text.lower()
    score = 0

    if "contrôle fiscal" in t:
        score += 30
    if "incohérence" in t:
        score += 25
    if "pas déclaré" in t:
        score += 30
    if "compte personnel" in t:
        score += 20
    if "justificatif" in t:
        score += 10

    score = min(score, 100)

    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"

    return score, level

# =========================
# COPILOT IA (LOGIQUE RULE-BASED V1)
# =========================
def copilot_analysis(text, score):

    t = text.lower()

    # =====================
    # ANALYSE JURIDIQUE
    # =====================
    if score > 70:
        legal = "Risque fiscal élevé de redressement avec incohérences déclaratives multiples."
    elif score > 40:
        legal = "Risque modéré nécessitant vérification des flux et déclarations."
    else:
        legal = "Risque faible, contrôle simple ou clarification administrative."

    # =====================
    # PIECES MANQUANTES
    # =====================
    missing = ["Relevés bancaires", "Factures clients"]

    if "compte personnel" in t:
        missing.append("Justificatifs séparation compte pro/perso")

    if "freelance" in t:
        missing.append("Contrats clients")

    # =====================
    # PLAN ACTION
    # =====================
    if score > 70:
        actions = [
            "Analyse urgente du dossier",
            "Reconstitution du chiffre d'affaires",
            "Préparation réponse administration",
            "Contact client immédiat"
        ]
    else:
        actions = [
            "Analyse dossier",
            "Vérification pièces",
            "Complément information client"
        ]

    # =====================
    # NOTE JURIDIQUE
    # =====================
    note = f"""
NOTE JURIDIQUE INTERNE

Résumé :
{legal}

Analyse :
Le dossier présente un score de risque de {score}/100.

Le traitement doit être réalisé sous supervision avocat.

Conclusion :
Dossier à analyser et sécuriser avant réponse administrative.
"""

    return legal, missing, actions, note

# =========================
# ROLE
# =========================
role = st.sidebar.selectbox("Mode utilisateur", ["Client", "Avocat"])

# =====================================================
# 👤 CLIENT MODE (UNCHANGED)
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique")

    name = st.text_input("Nom complet")
    email = st.text_input("Email")
    phone = st.text_input("Téléphone")
    company = st.text_input("Société")
    text = st.text_area("Votre situation")

    if name and text:

        if st.button("Envoyer"):

            score, level = compute_risk(text)

            conn = get_conn()
            c = conn.cursor()

            c.execute("""
            INSERT INTO dossiers 
            (client_name, email, phone, company, description, score, level, status)
            VALUES (?,?,?,?,?,?,?,?)
            """, (name, email, phone, company, text, score, level, "INCOMPLETE"))

            conn.commit()
            conn.close()

            st.success("📁 Dossier transmis au cabinet")
            st.info("Un avocat va analyser votre situation.")

# =====================================================
# ⚖️ AVOCAT MODE (COPILOT IA)
# =====================================================
else:

    st.title("⚖️ AI Copilot Avocat")

    conn = get_conn()
    c = conn.cursor()

    dossiers = c.execute("SELECT * FROM dossiers").fetchall()

    for d in dossiers:

        with st.expander(f"{d[1]} | Score {d[6]} ({d[7]})"):

            st.subheader("👤 Client")
            st.write("Nom:", d[1])
            st.write("Email:", d[2] or "N/A")
            st.write("Téléphone:", d[3] or "N/A")
            st.write("Société:", d[4] or "N/A")

            st.subheader("📄 Description")
            st.write(d[5])

            # =========================
            # COPILOT IA OUTPUT
            # =========================
            legal, missing, actions, note = copilot_analysis(d[5], d[6])

            st.subheader("🧠 Analyse juridique IA")
            st.write(legal)

            st.subheader("📎 Pièces manquantes")
            for m in missing:
                st.write("-", m)

            st.subheader("🧭 Plan d'action")
            for a in actions:
                st.write("-", a)

            st.subheader("📄 Note juridique interne")
            st.code(note)

            st.warning("⚠️ À valider par un avocat avant action")

    conn.close()
