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
        description TEXT,
        score INTEGER,
        level TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# IA
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
# SCORING
# =========================
def compute_risk(text):
    text = text.lower()
    score = 0
    reasons = []

    if "contrôle fiscal" in text:
        score += 30
        reasons.append("Contrôle fiscal engagé")

    if "incohérence" in text or "bancaire" in text:
        score += 25
        reasons.append("Incohérence revenus / flux bancaires")

    if "pas déclaré" in text or "pas tout déclaré" in text:
        score += 30
        reasons.append("Revenus non déclarés")

    if "compte personnel" in text:
        score += 20
        reasons.append("Mélange compte perso / pro")

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
# STRATEGY
# =========================
def generate_strategy(score):
    if score > 80:
        return [
            "⚠️ DOSSIER PRIORITAIRE",
            "Contacter le client immédiatement",
            "Demander relevés bancaires complets",
            "Reconstituer CA réel",
            "Préparer stratégie de défense"
        ]
    elif score > 50:
        return [
            "Analyser cohérence",
            "Compléter pièces",
            "Préparer réponse"
        ]
    else:
        return [
            "Vérification standard"
        ]

# =========================
# RECO
# =========================
def generate_recommendations(score):
    if score > 80:
        return [
            "Contact client immédiat",
            "Collecte documents complète",
            "Analyse fiscale détaillée"
        ]
    else:
        return [
            "Compléter dossier",
            "Analyse simple"
        ]

# =========================
# NOTE
# =========================
def generate_legal_note(text, score):
    return f"""
NOTE JURIDIQUE (INTERNE)

Situation :
Contrôle fiscal avec incohérence déclarative.

Risque :
Niveau {score}/100

Analyse :
Présence d’un risque de redressement fiscal.

Conclusion :
Dossier nécessitant traitement par avocat.
"""

# =========================
# DISCLAIMER
# =========================
def disclaimer():
    return """
⚠️ Cette analyse est générée par IA.
Elle doit être validée par un avocat avant toute action.
"""

# =========================
# ROLE
# =========================
role = st.sidebar.selectbox("Mode utilisateur", ["Client", "Avocat"])

# =====================================================
# CLIENT
# =====================================================
if role == "Client":

    st.title("👤 Assistant Juridique")

    st.write("""
Bonjour 👋  
Je vais vous aider à transmettre votre demande au cabinet.
""")

    name = st.text_input("Nom complet")
    text = st.text_area("Décrivez votre situation")

    if name and text:

        if st.button("Envoyer ma demande"):

            score, level, reasons = compute_risk(text)

            # SAVE
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "INSERT INTO dossiers (client_name, description, score, level) VALUES (?,?,?,?)",
                (name, text, score, level)
            )
            conn.commit()
            conn.close()

            # UI CLIENT SAFE
            st.success("📁 Votre demande a été envoyée")

            st.subheader("📄 Résumé")
            st.info("Votre situation a bien été transmise au cabinet.")

            st.subheader("📁 Suivi")
            st.write("Votre dossier est en cours d’analyse par un avocat.")
            st.write("Vous serez contacté prochainement.")

            st.subheader("📎 Documents à préparer")
            st.write("- relevés bancaires")
            st.write("- factures")
            st.write("- documents fiscaux")

            st.subheader("📞 Contact")
            email = st.text_input("Email")
            phone = st.text_input("Téléphone")

            st.divider()

            if st.button("🚨 Urgence - être rappelé"):
                st.warning("Demande prioritaire envoyée")

# =====================================================
# AVOCAT
# =====================================================
else:

    st.title("⚖️ Backoffice Avocat")

    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("SELECT * FROM dossiers").fetchall()

    if not rows:
        st.info("Aucun dossier")

    for r in rows:

        with st.expander(f"{r[1]} | Score {r[3]} ({r[4]})"):

            st.subheader("🧾 Description")
            st.write(r[2])

            st.subheader("⚠️ Score")
            st.metric("Score", r[3])
            st.write("Niveau :", r[4])

            st.subheader("⚖️ Stratégie")
            for s in generate_strategy(r[3]):
                st.write("-", s)

            st.subheader("📌 Actions")
            for rec in generate_recommendations(r[3]):
                st.write("-", rec)

            st.subheader("📄 Note juridique")
            st.code(generate_legal_note(r[2], r[3]))

            st.markdown(disclaimer())

    conn.close()
