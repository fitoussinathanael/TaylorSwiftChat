import streamlit as st
import sqlite3
from datetime import datetime
from io import BytesIO

# PDF (standard lib)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =========================
# CONFIG
# =========================
DB_PATH = "database.db"
st.set_page_config(page_title="JuriEngine V19 OS Cabinet", layout="wide")

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
# RISK ENGINE
# =========================
def compute_risk(text):
    t = text.lower()
    score = 0
    reasons = []

    if "contrôle fiscal" in t:
        score += 30
        reasons.append("Présence d’un contrôle fiscal (+30)")
    if "incohérence" in t:
        score += 25
        reasons.append("Incohérences déclaratives (+25)")
    if "compte personnel" in t:
        score += 20
        reasons.append("Flux sur compte personnel (+20)")
    if "pas déclaré" in t:
        score += 30
        reasons.append("Revenus non déclarés possibles (+30)")
    if "justificatif" in t:
        score += 10
        reasons.append("Demande de justificatifs (+10)")
    if "optimisation" in t:
        score += 5
        reasons.append("Demande optimisation (complexité +5)")

    score = min(score, 100)

    level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"

    return score, level, reasons

# =========================
# TYPE DETECTION
# =========================
def detect_type(text):
    t = text.lower()
    if "optimisation" in t:
        return "CONSEIL FISCAL STRATÉGIQUE"
    if "contrôle fiscal" in t or "redressement" in t:
        return "CONTENTIEUX FISCAL"
    return "FISCAL GÉNÉRAL"

# =========================
# SIMPLE RAG (SIMULÉ)
# =========================
def rag_simulation(query):
    base_knowledge = {
        "contrôle fiscal": "Un contrôle fiscal impose réponse sous délai + justificatifs structurés.",
        "optimisation fiscale": "L’optimisation est légale si absence d’abus de droit (article L64 LPF).",
        "tiers détenteur": "Une saisie administrative peut bloquer les comptes bancaires."
    }

    for k, v in base_knowledge.items():
        if k in query.lower():
            return v

    return "Aucune base juridique directe trouvée. Analyse avocat requise."

# =========================
# COPILOT AVOCAT (V19 + RAG + EXPLAINABILITY)
# =========================
def copilot(text, score):

    dtype = detect_type(text)
    rag = rag_simulation(text)
    _, _, reasons = compute_risk(text)

    explanation = "\n".join(reasons) if reasons else "Score basé sur absence de signaux forts."

    if dtype == "CONSEIL FISCAL STRATÉGIQUE":

        legal = "Dossier de structuration fiscale légale (hors contentieux)."

        docs = [
            "Structure juridique",
            "Flux financiers",
            "Bilan comptable",
            "Organisation activité"
        ]

        actions = [
            "Audit fiscal global",
            "Analyse optimisation légale",
            "Structuration juridique",
            "Recommandation régime fiscal"
        ]

        note = f"""
NOTE INTERNE CABINET

TYPE : {dtype}
SCORE : {score}/100

WHY THIS SCORE:
{explanation}

RAG:
{rag}

ANALYSE:
Optimisation légale possible sous réserve conformité.

⚠️ VALIDATION AVOCAT OBLIGATOIRE
"""

        return legal, docs, actions, note, dtype, explanation, rag

    # CONTENTIEUX
    legal = "Risque fiscal détecté"

    docs = ["Relevés bancaires", "Factures clients"]

    actions = [
        "Contacter client",
        "Collecter documents",
        "Analyser dossier",
        "Préparer réponse fiscale"
    ]

    note = f"""
NOTE INTERNE CABINET

TYPE : {dtype}
SCORE : {score}/100

WHY THIS SCORE:
{explanation}

RAG:
{rag}

⚠️ À VALIDER PAR AVOCAT
"""

    return legal, docs, actions, note, dtype, explanation, rag

# =========================
# PDF EXPORT (V18 FEATURE)
# =========================
def export_pdf(client, dossier, note):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.drawString(50, 800, "DOSSIER JURIDIQUE - EXPORT CABINET")
    p.drawString(50, 780, f"Client: {client}")
    p.drawString(50, 760, f"Date: {datetime.now()}")

    y = 720
    for line in note.split("\n"):
        p.drawString(50, y, line[:100])
        y -= 15
        if y < 100:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    return buffer

# =========================
# URGENCY CRM
# =========================
def create_urgent_ticket(name, email, phone, company, message):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO urgent_requests
    (client_name, email, phone, company, message)
    VALUES (?,?,?,?,?)
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

    send = col1.button("Envoyer")
    urgent = col2.button("🚨 Urgence avocat")

    if name and text and (send or urgent):

        score, level, reasons = compute_risk(text)

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
        INSERT INTO dossiers
        (client_name,email,phone,company,description,score,level,status)
        VALUES (?,?,?,?,?,?,?,?)
        """, (name,email,phone,company,text,score,level,"INCOMING"))

        conn.commit()
        conn.close()

        st.success("Dossier envoyé cabinet")

        st.subheader("🧠 Synthèse structurée")

        st.write("Type:", detect_type(text))
        st.write("Score:", score)

        st.markdown("### 🔎 Raisons du scoring")
        for r in reasons:
            st.write("•", r)

        st.markdown("### 📎 Documents")
        st.write("• Relevés bancaires")
        st.write("• Factures clients")
        st.write("• Déclarations fiscales")

        if urgent:
            create_urgent_ticket(name,email,phone,company,text)
            st.error("🚨 Urgence envoyée cabinet")

# =========================
# AVOCAT VIEW
# =========================
def lawyer_view():

    st.title("⚖️ OS Cabinet V19")

    conn = get_conn()
    c = conn.cursor()

    tab1, tab2 = st.tabs(["📁 Dossiers", "🚨 Urgences"])

    with tab1:

        dossiers = c.execute("SELECT * FROM dossiers").fetchall()

        for d in dossiers:

            legal, docs, actions, note, dtype, explain, rag = copilot(d[5], d[6])

            with st.expander(f"{d[1]} | {dtype} | {d[6]}/100"):

                st.write("👤", d[1])
                st.write("📞", d[3])

                st.subheader("🧠 IA")
                st.write(legal)

                st.subheader("🔎 Why score")
                st.code(explain)

                st.subheader("📚 RAG juridique")
                st.info(rag)

                st.subheader("📎 Docs")
                for x in docs:
                    st.write("•", x)

                st.subheader("🧭 Actions")
                for a in actions:
                    st.write("•", a)

                st.subheader("📄 Note juridique")
                st.code(note)

                # PDF EXPORT
                pdf = export_pdf(d[1], d, note)
                st.download_button(
                    "📄 Export PDF dossier",
                    pdf,
                    file_name=f"dossier_{d[0]}.pdf"
                )

    with tab2:

        urgents = c.execute("SELECT client_name,phone,email,company,message,created_at FROM urgent_requests").fetchall()

        for u in urgents:
            st.error(f"""
👤 {u[0]}
📞 {u[1]}
📄 {u[4]}
🕒 {u[5]}
""")

    conn.close()

# =========================
# ROUTER
# =========================
role = st.sidebar.selectbox("Mode", ["Client","Avocat"])

if role == "Client":
    client_view()
else:
    lawyer_view()
