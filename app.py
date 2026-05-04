import streamlit as st
import sqlite3
import os
from groq import Groq

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine", layout="wide")

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
        level TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# IA (optionnel safe)
# =========================
def get_ai():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)

def ai_analysis(text):
    client = get_ai()
    if not client:
        return "⚠️ IA non configurée"

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Avocat fiscaliste expert"},
                {"role": "user", "content": text}
            ]
        )
        return res.choices[0].message.content
    except:
        return "Erreur IA"

# =========================
# SCORING ENGINE
# =========================
def compute_risk(text):
    text = text.lower()
    score = 0
    reasons = []

    if "contrôle fiscal" in text:
        score += 30
        reasons.append("Contrôle fiscal")

    if "incohérence" in text or "bancaire" in text:
        score += 25
        reasons.append("Incohérence bancaire")

    if "pas déclaré" in text or "pas tout déclaré" in text:
        score += 30
        reasons.append("Revenus non déclarés")

    if "compte personnel" in text:
        score += 20
        reasons.append("Mélange compte perso/pro")

    if "justificatif" in text:
        score += 10
        reasons.append("Demande de justificatifs")

    score = min(score, 100)

    if score > 70:
        level = "HIGH"
    elif score > 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons

# =========================
# STRATEGY AVOCAT
# =========================
def generate_strategy(score):
    if score > 80:
        return [
            "DOSSIER PRIORITAIRE",
            "Contacter client immédiatement",
            "Collecter relevés bancaires",
            "Reconstitution CA",
            "Stratégie défense"
        ]
    elif score > 50:
        return [
            "Analyse dossier",
            "Compléter pièces",
            "Réponse administration"
        ]
    else:
        return ["Vérification standard"]

# =========================
# RECOMMANDATIONS
# =========================
def generate_recommendations(score):
    if score > 80:
        return [
            "Contact immédiat client",
            "Analyse fiscale complète",
            "Préparer régularisation"
        ]
    return ["Compléter dossier"]

# =========================
# NOTE JURIDIQUE
# =========================
def generate_legal_note(text, score):
    return f"""
NOTE INTERNE CABINET

Situation :
Contrôle fiscal avec incohérences déclaratives.

Score : {score}/100

Analyse :
Risque de redressement fiscal significatif.

Conclusion :
Dossier à traiter en priorité.
"""

# =========================
# DISCLAIMER
# =========================
def disclaimer():
    return """
⚠️ Analyse générée par IA.
Doit être validée par un avocat avant action.
"""

# =========================
# ROLE
# =========================
role = st.sidebar.selectbox("Mode utilisateur", ["Client", "Avocat"])

# =====================================================
# 👤 CLIENT MODE
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique du Cabinet")

    st.write("Bonjour 👋 Décrivez votre situation")

    # CRM INPUTS
    name = st.text_input("Nom complet")
    email = st.text_input("Email")
    phone = st.text_input("Téléphone")
    company = st.text_input("Société (optionnel)")

    text = st.text_area("Votre situation")

    if name and text:

        if st.button("Envoyer au cabinet"):

            score, level, reasons = compute_risk(text)

            conn = get_conn()
            c = conn.cursor()

            c.execute("""
            INSERT INTO dossiers 
            (client_name, email, phone, company, description, score, level)
            VALUES (?,?,?,?,?,?,?)
            """, (name, email, phone, company, text, score, level))

            conn.commit()
            conn.close()

            # UX CLIENT SIMPLIFIÉE
            st.success("📁 Votre demande a été envoyée au cabinet")

            st.subheader("📄 Résumé")
            st.info("Votre dossier est en cours d’analyse par un avocat.")

            st.subheader("📎 Documents à préparer")
            st.write("- relevés bancaires")
            st.write("- factures clients")
            st.write("- documents fiscaux")

            st.subheader("📞 Contact")
            st.write("Un avocat vous contactera rapidement.")

            if st.button("🚨 Urgence avocat"):
                st.warning("Demande prioritaire envoyée")

# =====================================================
# ⚖️ AVOCAT MODE
# =====================================================
else:

    st.title("⚖️ Backoffice Avocat")

    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("SELECT * FROM dossiers").fetchall()

    if not rows:
        st.info("Aucun dossier")

    for r in rows:

        with st.expander(f"{r[1]} | Score {r[6]} ({r[7]})"):

            # CRM CLIENT
            st.subheader("👤 Client")
            st.write("Nom :", r[1])
            st.write("Email :", r[2])
            st.write("Téléphone :", r[3])
            st.write("Société :", r[4])

            # DOSSIER
            st.subheader("📄 Description")
            st.write(r[5])

            st.subheader("⚠️ Score")
            st.metric("Score", r[6])
            st.write("Niveau :", r[7])

            # STRATEGY
            st.subheader("⚖️ Stratégie")
            for s in generate_strategy(r[6]):
                st.write("-", s)

            # RECO
            st.subheader("📌 Actions")
            for rec in generate_recommendations(r[6]):
                st.write("-", rec)

            # NOTE
            st.subheader("📄 Note juridique interne")
            st.code(generate_legal_note(r[5], r[6]))

            st.markdown(disclaimer())

    conn.close()
