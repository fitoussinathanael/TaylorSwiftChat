import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V3", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine V3")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["BASIC", "DOSE ICU", "INTERACTIONS", "AI SAFE"]
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
    # BASIC MODE
    # -----------------------------
    if mode == "BASIC":

        if context:

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
    # DOSE ICU MODE
    # -----------------------------
    elif mode == "DOSE ICU":

        drug = user_input.lower()

        doses = {
            "norad": "0.05 à 1 µg/kg/min",
            "nora": "0.05 à 1 µg/kg/min",
            "propof": "1 à 4 mg/kg/h",
            "fenta": "1 à 3 µg/kg/h",
            "midaz": "0.02 à 0.1 mg/kg/h"
        }

        dose = "non documenté pour ce médicament"

        for k, v in doses.items():
            if k in drug:
                dose = v

        answer = f"""
💉 MODE DOSE ICU

Médicament :
- {user_input}

Dose indicative :
- {dose}

⚠️ Adapter au poids, état hémodynamique et protocole local

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # INTERACTIONS MODE
    # -----------------------------
    elif mode == "INTERACTIONS":

        answer = f"""
🔗 MODE INTERACTIONS ICU

Entrée :
- {user_input}

Interactions connues :

- midazolam + opioïdes → dépression respiratoire ↑
- propofol + opioïdes → hypotension ↑
- noradrenaline + hypovolémie → inefficacité possible
- benzodiazépines + sédatifs → sédation profonde

⚠️ Liste simplifiée ICU V1

FIN : Cette analyse est une aide à la décision et ne remplace pas un professionnel de santé.
"""

    # -----------------------------
    # AI SAFE MODE
    # -----------------------------
    else:

        answer = f"""
🧠 MODE IA SAFE

Cas clinique :
- {user_input}

Données ICU :
{context if context else "non documenté"}

Analyse :
- mode IA préparé (LLM non activé encore)
- structure prête pour raisonnement clinique

⚠️ Version safe sans génération médicale avancée

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
