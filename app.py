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
except Exception as e:
    st.error("Clé API Groq manquante ou invalide")
    st.stop()

# -----------------------------
# SYSTEM PROMPT (ICU STRICT MODE)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un moteur ICU STRICT basé sur une base de données structurée.

RÈGLE ABSOLUE :
Tu dois utiliser UNIQUEMENT le CONTEXTE ICU fourni.

CONTEXTE STRUCTURÉ :
- Classe
- Usage
- Effets
- Surveillance
- Points ICU

RÈGLES :
- Tu recopies uniquement les informations présentes
- Tu n’ajoutes aucune connaissance externe
- Si une information manque → "non documenté dans la base ICU"

FORMAT OBLIGATOIRE :

Analyse clinique :
- Usage

Surveillance :
- Surveillance

Points de vigilance :
- Points ICU

FIN :
Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine — RAG Clinique")

# Reset
if st.sidebar.button("Reset session"):
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# HISTORIQUE
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT USER
# -----------------------------
user_input = st.chat_input("Entrez un médicament ou une situation ICU...")

if user_input:

    # save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        # sécurité fallback
        if not context or context.strip() == "":
            context = "non documenté dans la base ICU"

        # debug sidebar
        st.sidebar.subheader("📦 CONTEXTE ICU")
        st.sidebar.text(context)

        # -----------------------------
        # LLM CALL
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""
CONTEXTE ICU (DONNÉES STRUCTURÉES) :

{context}

QUESTION :
{user_input}
"""
                }
            ]
        )

        answer = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        st.error(f"Erreur LLM / API : {e}")
