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
# SYSTEM PROMPT (STRICT ICU)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un assistant clinique en réanimation infirmière.

RÈGLES ABSOLUES :
- utiliser UNIQUEMENT le contexte ICU fourni
- ne jamais inventer
- si info absente → dire : "non documenté dans la base ICU"

STRUCTURE OBLIGATOIRE :
- Analyse clinique
- Surveillance infirmière
- Points de vigilance

Finir par :
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
st.title("🏥 Hospital Engine — ICU RAG")
st.write("Système clinique structuré")

# -----------------------------
# MODE
# -----------------------------
mode = st.sidebar.selectbox(
    "Mode",
    ["urgence", "surveillance", "analyse", "pharmacologie"]
)

if st.sidebar.button("Nouvelle session"):
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
user_input = st.chat_input("Décris la situation...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        # -----------------------------
        # RAG ICU
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

IMPORTANT :
Réponds uniquement avec le CONTEXTE ICU.
Si absent → "non documenté dans la base ICU"

CONTEXTE :
{context}

QUESTION :
{user_input}
"""}
            ]
        )

        answer = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        st.error(f"Erreur : {e}")
