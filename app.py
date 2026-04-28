import streamlit as st
from groq import Groq
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine STRICT", page_icon="🏥")

# -----------------------------
# GROQ INIT
# -----------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API Groq manquante")
    st.stop()

# -----------------------------
# SYSTEM PROMPT STRICT
# -----------------------------
SYSTEM_PROMPT = """
Tu es un moteur ICU STRICT.

RÈGLE ABSOLUE :
Tu dois utiliser UNIQUEMENT le CONTEXTE ICU.

INTERDICTION :
- ajouter des connaissances
- compléter
- reformuler librement

INSTRUCTION :
- Tu copies les champs EXACTEMENT
- Si absent → "non documenté dans la base ICU"

FORMAT OBLIGATOIRE :

Analyse clinique :
- reprendre "usage"

Surveillance :
- reprendre "surveillance"

Points de vigilance :
- reprendre "points_icu"

NE RIEN AJOUTER.

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
st.title("🏥 ICU Engine — STRICT MODE")

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

        # DEBUG VISUEL
        st.sidebar.subheader("📦 CONTEXTE ICU")
        st.sidebar.write(context if context else "⚠️ VIDE")

        if not context:
            context = "non documenté dans la base ICU"

        # -----------------------------
        # LLM CALL (STRICT)
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
CONTEXTE ICU :
{context}

EXTRAIS UNIQUEMENT LES CHAMPS DEMANDÉS.
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
