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
# SYSTEM PROMPT (STRICT ICU)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un moteur ICU de restitution STRICTE.

RÈGLE ABSOLUE :
Tu dois utiliser UNIQUEMENT le CONTEXTE ICU fourni.
INTERDICTION totale d’utiliser des connaissances externes.

INSTRUCTION :
- Si une info est dans le contexte → tu la recopies fidèlement
- Si elle n’est pas dans le contexte → "non documenté dans la base ICU"

INTERDICTION :
- reformulation médicale libre
- ajout de connaissances générales
- extrapolation clinique

FORMAT OBLIGATOIRE :

Analyse clinique :
- uniquement contenu du contexte

Surveillance :
- uniquement contenu du contexte

Points de vigilance :
- uniquement contenu du contexte

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

mode = st.sidebar.selectbox(
    "Mode",
    ["urgence", "surveillance", "analyse", "pharmacologie"]
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
user_input = st.chat_input("Cas clinique ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        if "Aucune donnée" in context:
            context = "NON DOCUMENTÉ DANS LA BASE ICU"

        # DEBUG
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

CONTEXTE ICU (DONNÉES BRUTES - NE PAS REFORMULER) :

{context}

INSTRUCTION :
Copie exactement les champs du contexte ICU sans reformulation.

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
