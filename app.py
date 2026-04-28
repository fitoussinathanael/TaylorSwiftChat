import streamlit as st
from groq import Groq
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine", page_icon="🏥")

# -----------------------------
# GROQ INIT
# -----------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API Groq manquante")
    st.stop()

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
Tu es un assistant ICU basé STRICTEMENT sur un contexte fourni.

RÈGLES :
- Tu utilises uniquement le CONTEXTE ICU
- Si une info n'existe pas → "non documenté dans la base ICU"
- Tu n'inventes RIEN

FORMAT :

Analyse clinique :
-

Surveillance :
-

Points de vigilance :
-

FIN :
Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine")

mode = st.sidebar.selectbox(
    "Mode",
    ["urgence", "analyse", "surveillance", "pharmacologie"]
)

if st.sidebar.button("Reset"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# HISTORIQUE
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Entrez un médicament ou cas clinique ICU...")

if user_input:

    # affichage user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        # DEBUG VISUEL (IMPORTANT)
        st.sidebar.subheader("📦 CONTEXTE ICU")
        st.sidebar.write(context if context else "⚠️ VIDE")

        # sécurité si rien trouvé
        if not context:
            context = "non documenté dans la base ICU"

        # -----------------------------
        # LLM CALL
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
MODE: {mode}

CONTEXTE ICU (SOURCE UNIQUE) :
{context}

QUESTION :
{user_input}
"""}
            ]
        )

        answer = response.choices[0].message.content

        # affichage assistant
        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        st.error(f"Erreur : {e}")
