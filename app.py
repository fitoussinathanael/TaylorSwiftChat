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
except Exception:
    client = None
    st.warning("Mode BASIC uniquement (clé Groq manquante)")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI HEADER
# -----------------------------
st.title("🏥 ICU Engine — Multi Mode")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["BASIC", "AI"]
)

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
user_input = st.chat_input("Entrez un médicament ou un cas ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # -----------------------------
    # RAG ICU
    # -----------------------------
    context = search_icu(user_input)

    # sécurité
    if not context:
        context = None

    # -----------------------------
    # MODE BASIC (STRUCTURE FIXE)
    # -----------------------------
    if mode == "BASIC":

        if context:

            answer = f"""
Analyse clinique :
- {context['usage']}

Surveillance :
- {context['surveillance']}

Points de vigilance :
- {context['points_icu']}

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

        else:

            answer = """
Analyse clinique :
- non documenté dans la base ICU

Surveillance :
- non documenté dans la base ICU

Points de vigilance :
- non documenté dans la base ICU

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # MODE AI (LLM + RAG)
    # -----------------------------
    else:

        if not client:

            answer = "Mode AI indisponible (clé API manquante)."

        else:

            try:

                system_prompt = """
Tu es un assistant ICU clinique.

Tu utilises le contexte fourni pour produire une analyse médicale structurée.

RÈGLES :
- Utilise uniquement les informations du contexte ICU
- Si manque → "non documenté dans la base ICU"
- Ne pas inventer de données

FORMAT :

Analyse clinique :
Surveillance :
Points de vigilance :

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": f"""
CONTEXTE ICU :
{context}

CAS :
{user_input}
"""
                        }
                    ]
                )

                answer = response.choices[0].message.content

            except Exception as e:

                answer = f"Erreur LLM : {e}"

    # -----------------------------
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
