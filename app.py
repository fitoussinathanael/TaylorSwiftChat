import streamlit as st
import sqlite3
import json
from groq import Groq

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"

st.set_page_config(page_title="JuriEngine V20 OS Cabinet", layout="wide")

client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))

# =========================
# DB
# =========================
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS urgent_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        email TEXT,
        phone TEXT,
        company TEXT,
        message TEXT,
        status TEXT DEFAULT 'URGENT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# RISK ENGINE (EXPLICABLE)
# =========================
def compute_risk(text):
    t = text.lower()
    score = 0
    reasons = []

    if "contrôle fiscal" in t:
        score += 30
        reasons.append("Mention d’un contrôle fiscal (+30)")

    if "incohérence" in t:
        score += 25
        reasons.append("Incohérences déclarées (+25)")

    if "compte personnel" in t:
        score += 20
        reasons.append("Mélange compte personnel/pro (+20)")

    if "pas déclaré" in t:
        score += 30
        reasons.append("Risque de non-déclaration (+30)")

    if "justificatif" in t:
        score += 10
        reasons.append("Demande de justificatifs (+10)")

    if "optimisation" in t:
        reasons.append("Demande optimisation fiscale (non risquée)")

    score = min(score, 100)

    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"

    return score, level, reasons

# =========================
# AI ORCHESTRATOR (GROQ)
# =========================
def ai_orchestrator(text):

    system = """
Tu es un avocat fiscaliste senior assistant.
Tu analyses un dossier client.

Réponds STRICTEMENT en JSON :
{
  "type": "",
  "summary": "",
  "risks": [],
  "missing_documents": [],
  "actions": [],
  "legal_note": ""
}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {
            "type": "UNKNOWN",
            "summary": text,
            "risks": [],
            "missing_documents": [],
            "actions": ["Analyse manuelle requise"],
            "legal_note": "Erreur IA - fallback manuel"
        }

# =========================
# CHECKLIST
# =========================
def init_checklist(conn, dossier_id):
    c = conn.cursor()

    existing = c.execute(
        "SELECT COUNT(*) FROM checklist WHERE dossier_id=?",
        (dossier_id,)
    ).fetchone()[0]

    if existing == 0:
        tasks = [
            "Contacter client",
            "Collecter documents",
            "Analyser dossier",
            "Préparer réponse fiscale"
        ]

        for t in tasks:
            c.execute(
                "INSERT INTO checklist (dossier_id, task, done) VALUES (?,?,0)",
                (dossier_id, t)
            )

# =========================
# URGENT CRM
# =========================
def create_urgent_ticket(name, email, phone, company, message):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO urgent_requests
    (client_name, email, phone, company, message, status)
    VALUES (?,?,?,?,?, 'URGENT')
    """, (name, email, phone, company, message))

    conn.commit()
    conn.close()

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

    col1, col2 = st.columns(2)

    send = col1.button("Envoyer au cabinet")
    urgent = col2.button("🚨 URGENCE - rappel avocat")

    if name and text and (send or urgent):

        score, level, reasons = compute_risk(text)
        ai = ai_orchestrator(text)

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        INSERT INTO dossiers
        (client_name, email, phone, company, description, score, level, status)
        VALUES (?,?,?,?,?,?,?,?)
        """, (name, email, phone, company, text, score, level, "INCOMING"))

        conn.commit()
        conn.close()

        st.success("Dossier transmis au cabinet")

        # =========================
        # SYNTHÈSE CLIENT
        # =========================
        st.subheader("🧠 Synthèse structurée")

        st.write("📌 Type :", ai["type"])
        st.write("📊 Score :", score)
        st.write("📊 Niveau :", level)

        st.markdown("### 📄 Résumé IA")
        st.write(ai["summary"])

        st.markdown("### ⚠️ Raisons du score")
        for r in reasons:
            st.write("•", r)

        st.markdown("### 📎 Documents à préparer")
        for d in ai["missing_documents"]:
            st.write("•", d)

        st.markdown("### 🧭 Actions")
        for a in ai["actions"]:
            st.write("•", a)

        # =========================
        # URGENCE CRM
        # =========================
        if urgent:
            create_urgent_ticket(name, email, phone, company, text)

            st.error("🚨 URGENCE envoyée")

            st.info(f"""
📞 CONTACT PRIORITAIRE

Nom : {name}
Téléphone : {phone}
Email : {email}
""")

# =========================
# AVOCAT VIEW
# =========================
def lawyer_view():

    st.title("⚖️ OS Cabinet V20 - AI Orchestrator")

    conn = get_conn()
    c = conn.cursor()

    tab1, tab2 = st.tabs(["📁 Dossiers", "🚨 Urgences"])

    with tab1:

        dossiers = c.execute("SELECT * FROM dossiers").fetchall()

        for d in dossiers:

            ai = ai_orchestrator(d[5])

            with st.expander(f"{d[1]} | Score {d[6]}"):

                st.write("👤", d[1])
                st.write("📞", d[3])
                st.write("📄", d[5])

                st.subheader("🧠 IA")
                st.write(ai["summary"])

                st.subheader("📎 Docs")
                for x in ai["missing_documents"]:
                    st.write("•", x)

                st.subheader("🧭 Actions")
                for a in ai["actions"]:
                    st.write("•", a)

                st.subheader("📄 Note juridique")
                st.write(ai["legal_note"])

    with tab2:

        urgent = c.execute("SELECT * FROM urgent_requests").fetchall()

        for u in urgent:
            st.error(f"""
👤 {u[1]}
📞 {u[3]}
📄 {u[5]}
""")

    conn.close()

# =========================
# ROUTING
# =========================
role = st.sidebar.selectbox("Mode", ["Client", "Avocat"])

if role == "Client":
    client_view()
else:
    lawyer_view()
