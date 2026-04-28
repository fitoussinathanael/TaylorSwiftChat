import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine — RAG Stable")

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

    # -----------------------------
    # RAG ICU
    # -----------------------------
    context = search_icu(user_input)

    # sécurité
    if not context or "non documenté" in context:
        answer = """
Analyse clinique :
- non documenté dans la base ICU

Surveillance :
- non documenté dans la base ICU

Points de vigilance :
- non documenté dans la base ICU

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""
    else:
        # -----------------------------
        # FORMATAGE 100% PYTHON (IMPORTANT)
        # -----------------------------
        try:
            # extraction simple depuis texte RAG
            lines = context.split("\n")

            usage = ""
            surveillance = ""
            points = ""

            for i, line in enumerate(lines):
                if "Usage" in line:
                    usage = line.split(":", 1)[-1].strip()
                if "Surveillance" in line:
                    surveillance = line.split(":", 1)[-1].strip()
                if "Points ICU" in line:
                    points = line.split(":", 1)[-1].strip()

            answer = f"""
Analyse clinique :
- {usage if usage else "non documenté dans la base ICU"}

Surveillance :
- {surveillance if surveillance else "non documenté dans la base ICU"}

Points de vigilance :
- {points if points else "non documenté dans la base ICU"}

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

        except Exception:
            answer = """
Analyse clinique :
- erreur de parsing ICU

Surveillance :
- erreur de parsing ICU

Points de vigilance :
- erreur de parsing ICU

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
