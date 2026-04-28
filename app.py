import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG (TOUJOURS EN PREMIER)
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
st.title("🏥 ICU Engine - Stable V1")

mode = st.sidebar.selectbox("Mode ICU", ["BASIC"])

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
user_input = st.chat_input("Tape un médicament ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # -----------------------------
    # RAG
    # -----------------------------
    context = search_icu(user_input)

    # -----------------------------
    # SAFE OUTPUT (AUCUN CRASH POSSIBLE)
    # -----------------------------
    if context is not None:

        answer = f"""
Analyse clinique :
- {context.get('usage', 'non documenté dans la base ICU')}

Surveillance :
- {context.get('surveillance', 'non documenté dans la base ICU')}

Points de vigilance :
- {context.get('points_icu', 'non documenté dans la base ICU')}

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
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
