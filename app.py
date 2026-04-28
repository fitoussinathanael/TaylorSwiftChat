import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V2", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine V2")

mode = st.sidebar.selectbox(
    "Mode",
    ["BASIC", "DOSE ICU", "INTERACTIONS", "AI (safe)"]
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
user_input = st.chat_input("Cas ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    context = search_icu(user_input)

    # -----------------------------
    # MODE BASIC
    # -----------------------------
    if mode == "BASIC":

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
    # MODE DOSE ICU (simple V1)
    # -----------------------------
    elif mode == "DOSE ICU":

        answer = f"""
💉 MODE DOSE ICU

Médicament détecté :
- {user_input}

⚠️ Version simplifiée (V1)

Si noradrenaline :
- dose typique : 0.05 à 1 µg/kg/min

Si propofol :
- 1 à 4 mg/kg/h

Si fentanyl :
- 1 à 3 µg/kg/h

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # MODE INTERACTIONS
    # -----------------------------
    elif mode == "INTERACTIONS":

        answer = f"""
🔗 MODE INTERACTIONS ICU

Analyse entrée :
- {user_input}

Interactions connues (V1 simplifiée) :

- midazolam + opioïdes → dépression respiratoire ↑
- propofol + hypotension → effet additif
- noradrenaline + hypovolémie → inefficacité possible

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # MODE AI SAFE (placeholder)
    # -----------------------------
    else:

        answer = f"""
🧠 MODE IA (SAFE V1)

Analyse du cas :
- {user_input}

Contexte ICU :
{context if context else "non documenté"}

⚠️ Mode IA non encore activé (prochaine étape)

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
