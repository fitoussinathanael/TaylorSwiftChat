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
# SYSTEM PROMPT (SAFE VERSION)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un moteur ICU STRICT.

Tu dois utiliser UNIQUEMENT le CONTEXTE ICU.

RÈGLES :
- Tu copies uniquement les lignes présentes
- Si absent → "non documenté dans la base ICU"
- Tu n’ajoutes rien

FORMAT :

Analyse clinique :
- reprendre ligne "Usage"

Surveillance :
- reprendre ligne "Surveillance"

Points de vigilance :
- reprendre ligne "Points ICU"

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

if st.sidebar.button("Reset"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Entrez un médicament ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        # DEBUG
        st.sidebar.subheader("📦 CONTEXTE ICU")
        st.sidebar.write(context if context else "⚠️ VIDE")

        if not context:
            context = "non documenté dans la base ICU"

        # -----------------------------
        # LLM
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
CONTEXTE ICU :
{context}
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
