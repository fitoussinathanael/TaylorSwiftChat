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
# SYSTEM PROMPT (CLEAN + REALISTIC)
# -----------------------------
SYSTEM_PROMPT = """
Tu es un assistant ICU basé UNIQUEMENT sur un contexte fourni.

RÈGLES :
- Utilise uniquement les données du contexte ICU
- Si une information manque → écrire "non documenté dans la base ICU"
- Ne pas inventer de connaissances médicales

FORMAT :

Analyse clinique :
- basée uniquement sur le contexte

Surveillance :
- basée uniquement sur le contexte

Points de vigilance :
- basés uniquement sur le contexte

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

        # 🔥 FIX IMPORTANT : NE PAS ÉCRASER LE CONTEXTE
        if not context or "Aucune donnée ICU trouvée" in context:
            context = "AUCUNE DONNÉE ICU TROUVÉE DANS LA BASE"

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
TU ES EN MODE EXTRACTION STRICTE.

RÈGLE ABSOLUE :
Tu ne peux utiliser QUE les informations ci-dessous.

Si une info n'est pas présente → écris "non documenté dans la base ICU"

-------------------------
CONTEXTE ICU (SOURCE UNIQUE AUTORISÉE)
-------------------------
{context}
-------------------------

FORMAT OBLIGATOIRE :

Analyse clinique :
-

Surveillance :
-

Points de vigilance :
-

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
        st.error(f"Erreur: {e}")
