import streamlit as st
from groq import Groq

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Hospital Engine ICU", page_icon="🏥")

# -----------------------------
# GROQ INIT
# -----------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API Groq manquante dans st.secrets")
    st.stop()

# -----------------------------
# SYSTEM PROMPT (SAFE + STABLE)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un assistant clinique en réanimation.

Règles :
- répondre de façon structurée
- ne pas inventer de données précises si non fournies
- distinguer analyse / surveillance / vigilance

Format :
Analyse clinique :
Surveillance :
Points de vigilance :

Fin :
"Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé."
"""

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 Hospital Engine ICU")
st.write("Assistant clinique de réanimation (version stable)")

# -----------------------------
# MODE
# -----------------------------
mode = st.sidebar.selectbox(
    "Mode",
    ["urgence", "surveillance", "analyse", "transmission", "pharmacologie"]
)

if st.sidebar.button("Nouvelle session"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# DISPLAY HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Décris la situation clinique...")

if user_input:

    # user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # LLM CALL SIMPLE (SANS RAG)
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Mode: {mode}\n\nCas clinique:\n{user_input}"}
            ]
        )

        answer = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        st.error(f"Erreur API : {e}")
