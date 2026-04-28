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
st.title("🏥 ICU Engine V5 - Clinical Support Tool")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION ICU REAL"]
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

    # =========================================================
    # ⚡ QUICK ICU MODE
    # =========================================================
    if mode == "QUICK ICU":

        if context:

            answer = f"""
⚡ QUICK ICU

💊 Médicament : {user_input}

→ Usage : {context.get('usage', 'non documenté')}
→ Surveillance : {context.get('surveillance', 'non documenté')}
→ ⚠️ Vigilance : {context.get('points_icu', 'non documenté')}

👉 Action : surveillance clinique rapprochée selon protocole local
"""

        else:

            answer = """
⚡ QUICK ICU

→ Médicament non documenté dans la base ICU
→ Vérification requise
"""

    # =========================================================
    # 💉 PERFUSION ICU RÉEL (SIMPLIFIÉ MAIS COHÉRENT)
    # =========================================================
    else:

        text = user_input.lower()

        # poids patient (default)
        weight = 70
        for w in text.split():
            if w.isdigit():
                weight = int(w)

        # concentrations standards simplifiées ICU
        drugs = {
            "norad": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160},
            "nora": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160},
            "propof": {"dose": 2, "unit": "mg/kg/h", "conc": 10},
            "fenta": {"dose": 2, "unit": "µg/kg/h", "conc": 50},
            "midaz": {"dose": 0.05, "unit": "mg/kg/h", "conc": 1}
        }

        found = None
        for k in drugs:
            if k in text:
                found = k
                break

        if found:

            d = drugs[found]

            # NORAD / FENTANYL (µg)
            if "µg" in d["unit"]:

                ug_h = d["dose"] * weight * 60
                ml_h = ug_h / d["conc"]

            # PROPOFOL / MIDAZ (mg)
            else:

                mg_h = d["dose"] * weight
                ml_h = mg_h / d["conc"]

            answer = f"""
💉 PERFUSION ICU (SIMPLIFIÉ)

Médicament : {found}
Poids : {weight} kg

Dose : {d['dose']} {d['unit']}
Concentration : {d['conc']} (standard ICU simplifié)

👉 Débit estimé : {round(ml_h, 2)} mL/h

⚠️ À adapter selon protocole local + seringue électrique + état clinique
"""

        else:

            answer = """
💉 PERFUSION ICU

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
