import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V6", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine V6 - Clinical Decision Support")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION ICU REAL", "IA CLINIQUE"]
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
    # 💉 PERFUSION ICU RÉEL
    # =========================================================
    elif mode == "PERFUSION ICU REAL":

        text = user_input.lower()

        weight = 70
        for w in text.split():
            if w.isdigit():
                weight = int(w)

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

            if "µg" in d["unit"]:

                ug_h = d["dose"] * weight * 60
                ml_h = ug_h / d["conc"]

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

⚠️ Adapter au protocole local + état clinique
"""

        else:

            answer = """
💉 PERFUSION ICU

Médicament non reconnu pour calcul automatique
"""

    # =========================================================
    # 🧠 IA CLINIQUE MODE
    # =========================================================
    else:

        answer = f"""
🧠 IA CLINIQUE ICU

📌 Cas patient :
{user_input}

📦 Données ICU :
{context if context else "non documenté dans la base ICU"}

---

🔍 SYNTHÈSE CLINIQUE :

- Analyse du contexte clinique en cours
- Corrélation médicaments / hémodynamique / sédation
- Évaluation des risques ICU (hypotension, dépression respiratoire, sédation excessive)

---

⚠️ POINTS DE VIGILANCE :

- Surveillance hémodynamique rapprochée (TA / FC)
- Adapter la sédation selon état neurologique et ventilation
- Vérifier interactions médicamenteuses potentielles

---

👉 ACTIONS GÉNÉRALES :

- Vérifier perfusions actives
- Réévaluer constantes vitales
- Ajuster traitements selon protocole réanimation

---

FIN : outil d’aide à la décision, ne remplace pas jugement médical.
"""

    # -----------------------------
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
