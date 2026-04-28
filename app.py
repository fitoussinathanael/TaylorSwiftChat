import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Quick Tool", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Quick Tool V4")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION CALC"]
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
user_input = st.chat_input("Entrée ICU...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    context = search_icu(user_input)

    # -----------------------------
    # QUICK ICU MODE
    # -----------------------------
    if mode == "QUICK ICU":

        if context:

            answer = f"""
⚡ QUICK ICU

💊 {user_input}

→ Usage : {context.get('usage', 'non documenté')}
→ Surveillance : {context.get('surveillance', 'non documenté')}
→ ⚠ {context.get('points_icu', 'non documenté')}

👉 Action : vérifier protocole local + surveillance rapprochée

"""

        else:

            answer = """
⚡ QUICK ICU

→ Médicament non documenté dans la base ICU
→ Vérification requise

"""

    # -----------------------------
    # PERFUSION CALCULATOR
    # -----------------------------
    else:

        text = user_input.lower()

        weight = 70  # valeur par défaut

        # extraction simple poids
        for word in text.split():
            if word.isdigit():
                weight = int(word)

        if "norad" in text:
            dose = 0.2  # µg/kg/min exemple
            result = weight * dose * 0.06  # simplification mL/h

        elif "propof" in text:
            dose = 2
            result = weight * dose / 10

        elif "fenta" in text:
            dose = 2
            result = weight * dose / 100

        else:
            result = None

        if result:

            answer = f"""
💉 PERFUSION CALCUL

Médicament : {user_input}
Poids : {weight} kg

👉 Débit estimé : {round(result, 2)} mL/h

⚠️ Vérifier concentration et protocole local

"""

        else:

            answer = """
💉 PERFUSION CALCUL

Médicament non reconnu pour calcul automatique

"""

    # -----------------------------
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
