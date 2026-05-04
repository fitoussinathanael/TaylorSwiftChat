import streamlit as st
import sqlite3
import os
from groq import Groq

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine V8", layout="wide")

# =========================
# DB LAYER
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
        description TEXT,
        score INTEGER,
        level TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# IA (SAFE)
# =========================
def get_ai_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def ai_analysis(text):
    client = get_ai_client()

    if not client:
        return "⚠️ IA non configurée (clé GROQ manquante)"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un avocat fiscaliste expert."},
                {"role": "user", "content": f"Analyse ce cas fiscal : {text}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Erreur IA : {str(e)}"

# =========================
# SCORING ENGINE
# =========================
def compute_risk(text):
    text = text.lower()

    score = 0
    reasons = []

    # 🔴 contrôle fiscal
    if "contrôle fiscal" in text:
        score += 30
        reasons.append("Contrôle fiscal engagé")

    # 🔴 incohérence bancaire
    if "incohérence" in text or "bancaire" in text:
        score += 25
        reasons.append("Incohérence revenus / flux bancaires")

    # 🔴 revenus non déclarés (CRITIQUE)
    if "pas déclaré" in text or "pas tout déclaré" in text:
        score += 30
        reasons.append("Suspicion de revenus non déclarés")

    # 🔴 mélange comptes (ULTRA IMPORTANT)
    if "compte personnel" in text:
        score += 20
        reasons.append("Mélange compte personnel / professionnel")

    # 🟠 TVA
    if "tva" in text:
        score += 15
        reasons.append("Risque TVA")

    # 🟠 justificatifs
    if "justificatif" in text:
        score += 10
        reasons.append("Demande de justificatifs")

    # 🔴 redressement
    if "redressement" in text:
        score += 20
        reasons.append("Risque de redressement")

    score = min(score, 100)

    # niveau
    if score > 70:
        level = "HIGH"
    elif score > 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons

# =========================
# CHECKLIST
# =========================
def generate_checklist(text):
    text = text.lower()

    checklist = [
        "Relevés bancaires",
        "Factures clients",
        "Contrats clients",
        "Justificatifs comptables"
    ]

    if "tva" in text:
        checklist += [
            "Déclarations TVA",
            "Livre de recettes"
        ]

    return list(set(checklist))

# =========================
# TIMELINE
# =========================
def generate_timeline(score):

    if score > 60:
        return [
            "⚡ Répondre rapidement à l'administration",
            "Collecter toutes les pièces",
            "Analyser les incohérences",
            "Préparer la stratégie de défense"
        ]

    elif score > 30:
        return [
            "Collecter les documents",
            "Analyser la situation",
            "Vérifier conformité fiscale",
            "Préparer réponse"
        ]

    else:
        return [
            "Collecte simple des documents",
            "Vérification de base",
            "Suivi du dossier"
        ]

# =========================
# ROLE SYSTEM
# =========================
role = st.sidebar.selectbox(
    "Mode utilisateur",
    ["Client", "Avocat"]
)

# =====================================================
# 👤 MODE CLIENT
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique du Cabinet")

    st.write("""
Bonjour 👋  
Je suis votre assistant juridique.

Je vais vous aider à :
- analyser votre situation fiscale
- structurer votre dossier
- identifier les risques
- préparer les actions à mener
""")

    st.divider()

    client_name = st.text_input("Nom complet")
    client_text = st.text_area(
        "Décrivez votre situation",
        placeholder="Ex : contrôle fiscal TVA, incohérence revenus..."
    )

    if client_name and client_text:

        if st.button("Analyser ma situation"):

            st.info("Analyse en cours...")

            # SCORING
            score, level, reasons = compute_risk(client_text)

            # CHECKLIST
            checklist = generate_checklist(client_text)

            # TIMELINE
            timeline = generate_timeline(score)

            # SAVE DOSSIER
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "INSERT INTO dossiers (client_name, description, score, level) VALUES (?,?,?,?)",
                (client_name, client_text, score, level)
            )
            conn.commit()
            conn.close()

            st.success("📁 Dossier créé automatiquement")

            # DISPLAY
            st.subheader("⚠️ Score de risque")
            st.metric("Score", score)
            st.write("Niveau :", level)

            st.write("### Raisons")
            for r in reasons:
                st.write("-", r)

            st.subheader("📎 Pièces à fournir")
            for item in checklist:
                st.write("-", item)

            st.subheader("🧭 Plan d'action")
            for step in timeline:
                st.write("-", step)

            st.subheader("🧠 Analyse juridique IA")
            st.write(ai_analysis(client_text))


# =====================================================
# ⚖️ MODE AVOCAT
# =====================================================
else:

    st.title("⚖️ Backoffice Avocat")

    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("SELECT * FROM dossiers").fetchall()

    if not rows:
        st.info("Aucun dossier pour le moment")

    for r in rows:

        with st.expander(f"{r[1]} | Score {r[3]} ({r[4]})"):

            st.write("### Description")
            st.write(r[2])

            st.write("### Score de risque")
            st.metric("Score", r[3])
            st.write("Niveau :", r[4])

    conn.close()
