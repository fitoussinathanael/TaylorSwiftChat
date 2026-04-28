import streamlit as st
from groq import Groq
from rag_icu import search_icu

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
# SYSTEM PROMPT STRICT ICU
# -----------------------------
SYSTEM_PROMPT = """
Tu es un moteur ICU STRICT.

RÈGLES ABSOLUES :
- Tu n’as accès QU’AU CONTEXTE ICU fourni
- INTERDICTION d’utiliser des connaissances externes
- Ne jamais inventer

SI information absente :
→ écrire EXACTEMENT : "non documenté dans la base ICU"

FORMAT OBLIGATOIRE :

Analyse clinique :
Surveillance :
Points de vigilance :

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
st.title("🏥 ICU Engine — RAG")
st.write("Système de support clinique réanimation")

mode = st.sidebar.selectbox(
    "Mode",
    ["urgence", "surveillance", "analyse", "pharmacologie"]
)

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
# INPUT
# -----------------------------
user_input = st.chat_input("Cas clinique...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        # SI VIDE → blocage propre
        if "Aucune donnée" in context:
            context = "NON DOCUMENTÉ DANS LA BASE ICU"

        # DEBUG (sidebar)
        st.sidebar.subheader("📦 CONTEXTE ICU")
        st.sidebar.text(context)

        # -----------------------------
        # LLM CALL
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
MODE: {mode}

CONTEXTE ICU:
{context}

QUESTION:
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
        st.error(f"Erreur: {e}")
