import streamlit as st
from rag_icu import search_icu

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ICU Engine V8", page_icon="🏥")

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("🏥 ICU Engine V8 - Clinical AI + Terrain")

mode = st.sidebar.selectbox(
    "Mode ICU",
    ["QUICK ICU", "PERFUSION ICU REAL", "PERFUSION TERRAIN", "IA CLINIQUE"]
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
    # ⚡ QUICK ICU
    # =========================================================
    if mode == "QUICK ICU":

        if context and context != "non documenté dans la base ICU":

            answer = f"""
⚡ QUICK ICU

💊 Médicament : {user_input}

📦 Données :
{context}

👉 Action : surveillance clinique selon protocole
"""

        else:

            answer = """
⚡ QUICK ICU

→ Médicament non documenté dans la base ICU
"""

    # =========================================================
    # 💉 PERFUSION ICU REAL
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
💉 PERFUSION ICU REAL

Médicament : {found}
Poids : {weight} kg

Dose : {d['dose']} {d['unit']}
Concentration : {d['conc']}

👉 Débit exact : {round(ml_h, 2)} mL/h

⚠️ Vérifier protocole local
"""

        else:

            answer = """
💉 PERFUSION ICU

Médicament non reconnu
"""

    # =========================================================
    # 🏥 PERFUSION TERRAIN (NOUVEAU 🔥)
    # =========================================================
    elif mode == "PERFUSION TERRAIN":

        text = user_input.lower()

        weight = 70
        for w in text.split():
            if w.isdigit():
                weight = int(w)

        drugs = {
            "norad": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160, "label": "noradrénaline"},
            "nora": {"dose": 0.1, "unit": "µg/kg/min", "conc": 160, "label": "noradrénaline"},
            "propof": {"dose": 2, "unit": "mg/kg/h", "conc": 10, "label": "propofol"},
            "fenta": {"dose": 2, "unit": "µg/kg/h", "conc": 50, "label": "fentanyl"},
            "midaz": {"dose": 0.05, "unit": "mg/kg/h", "conc": 1, "label": "midazolam"}
        }

        found = None
        for k in drugs:
            if k in text:
                found = k
                break

        if found:

            d = drugs[found]

            # calcul réel
            if "µg" in d["unit"]:
                ug_h = d["dose"] * weight * 60
                ml_h = ug_h / d["conc"]
            else:
                mg_h = d["dose"] * weight
                ml_h = mg_h / d["conc"]

            # ARRONDI TERRAIN (0.5 mL/h)
            ml_h_round = round(ml_h * 2) / 2

            answer = f"""
🏥 PERFUSION TERRAIN

Médicament : {d['label']}
Poids : {weight} kg

👉 Débit proposé : {ml_h_round} mL/h

(≈ {round(ml_h,2)} mL/h calculé)

✔ valeur arrondie utilisable IDE
✔ cohérence pratique terrain

⚠️ Vérifier protocole du service
"""

        else:

            answer = """
🏥 PERFUSION TERRAIN

Médicament non reconnu
"""

    # =========================================================
    # 🧠 IA CLINIQUE ADAPTATIVE
    # =========================================================
    else:

        text = user_input.lower()

        risks = []
        actions = []

        if "hypotension" in text:
            risks.append("instabilité hémodynamique")
            actions.append("évaluer remplissage + ajuster vasopresseur")

        if "propof" in text:
            risks.append("hypotension induite par sédation")
            actions.append("réévaluer dose propofol")

        if "norad" in text or "nora" in text:
            risks.append("choc circulatoire")
            actions.append("adapter titration noradrénaline")

        if "midazolam" in text or "fentanyl" in text:
            risks.append("sédation excessive / dépression respiratoire")
            actions.append("contrôler RASS")

        if "choc" in text or "septique" in text:
            risks.append("état de choc")
            actions.append("optimiser perfusion + support hémodynamique")

        if "intubé" in text or "ventilation" in text:
            risks.append("dépendance ventilatoire")
            actions.append("surveiller ventilation")

        if not risks:
            risks.append("analyse clinique nécessaire")

        if not actions:
            actions.append("surveillance ICU standard")

        answer = f"""
🧠 IA CLINIQUE ICU (ADAPTATIVE)

📌 Cas :
{user_input}

📦 Données ICU :
{context if context else "non documenté"}

---

🚨 RISQUES :
- {"\n- ".join(risks)}

---

👉 ACTIONS :
- {"\n- ".join(actions)}

---

🔍 SURVEILLANCE :
- TA / FC
- neurologique
- ventilation

---

FIN : aide à la décision
"""

    # -----------------------------
    # OUTPUT
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
