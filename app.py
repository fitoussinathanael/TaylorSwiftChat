import streamlit as st
from groq import Groq
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Hospital Engine", page_icon="🏥")

# -----------------------------
# GROQ INIT
# -----------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API Groq manquante.")
    st.stop()

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
SYSTEM PROMPT — HOSPITAL ENGINE V4

Tu es un assistant clinique spécialisé en réanimation infirmière.

Tu aides à :
- structurer les transmissions
- analyser des situations cliniques
- sécuriser la pharmacologie
- calculer des doses
- réduire la charge mentale

RÈGLES :
- ne jamais inventer
- toujours distinguer faits / interprétation / actions
- privilégier sécurité patient
- si doute → dire incertain

MODES :
urgence / surveillance / analyse / transmission / pharmacologie / calcul / recueil / dossier / garde / swiftie

Si mode = pharmacologie :
→ utiliser uniquement données fournies
→ sinon dire "non documenté"

Si mode = transmission :
→ structurer en DAR par cibles :
respiratoire / hémodynamique / neurologique / infectieux / rénal / métabolique / dispositifs

Si mode = calcul :
→ proposer adaptation pratique avec débits simples

Toujours terminer par :
"Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé."
"""

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 Hospital Engine — Réanimation")
st.write("Assistant clinique intelligent pour infirmière de réanimation")

# -----------------------------
# MODE SELECT
# -----------------------------
mode = st.sidebar.selectbox(
    "Mode",
    [
        "urgence",
        "surveillance",
        "analyse",
        "transmission",
        "pharmacologie",
        "calcul",
        "recueil",
        "dossier",
        "garde",
        "swiftie"
    ]
)

# Reset
if st.sidebar.button("Nouvelle session"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# DISPLAY HISTORY
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Décris la situation...")

if user_input:

    # Affichage user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # 🧠 RAG ICU CONTEXT
        # -----------------------------
        context = search_icu(user_input)

        # -----------------------------
        # LLM CALL
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
MODE: {mode}

CONTEXTE ICU (BASE STRUCTURÉE):
{context}

QUESTION:
{user_input}
"""}
            ]
        )

        assistant_reply = response.choices[0].message.content

        # Affichage assistant
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_reply}
        )

    except Exception as e:
        st.error(f"Erreur : {e}")
