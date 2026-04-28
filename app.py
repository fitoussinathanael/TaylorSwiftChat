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
Tu es un assistant clinique spécialisé en réanimation infirmière ICU.

RÈGLES STRICTES :
- ne jamais inventer de données médicales
- utiliser le contexte ICU fourni
- si information absente → dire "non documenté"
- séparer faits / interprétation / actions
- privilégier sécurité patient

STRUCTURE DE RÉPONSE :
- Analyse clinique
- Points de vigilance
- Conduite infirmière
- Conclusion

TOUJOURS terminer par :
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
st.title("🏥 Hospital Engine — ICU Assistant")
st.write("Assistant clinique pour réanimation infirmière")

# -----------------------------
# CHAT INPUT
# -----------------------------
user_input = st.chat_input("Décris la situation clinique...")

if user_input:

    # afficher user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # -----------------------------
        # RAG ICU
        # -----------------------------
        context = search_icu(user_input)

        # sécurité si RAG vide
        if not context:
            context = "Aucune donnée ICU disponible"

        # -----------------------------
        # LLM CALL
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
CONTEXTE ICU (BASE STRUCTURÉE):
{context}

QUESTION CLINIQUE:
{user_input}

IMPORTANT ABSOLU :
Tu dois utiliser le CONTEXTE ICU fourni comme source UNIQUE.
Si une information n’est pas dans ce contexte → répondre "non documenté dans la base ICU".
Ne pas utiliser de connaissances externes.
Si absent → répondre "non documenté dans la base ICU".
"""}
            ]
        )

        assistant_reply = response.choices[0].message.content

        # affichage assistant
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_reply}
        )

    except Exception as e:
        st.error(f"Erreur : {e}")

# -----------------------------
# RESET
# -----------------------------
if st.sidebar.button("Nouvelle session"):
    st.session_state.messages = []
    st.rerun()
