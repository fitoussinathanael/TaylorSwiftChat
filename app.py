import streamlit as st
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V8", page_icon="🏥", layout="wide")

# =========================================================
# HEADER
# =========================================================
st.title("🏥 ICU ENGINE")
st.caption("ICU FLOW decision support - stable mode")

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "patients" not in st.session_state:
    st.session_state.patients = {}

if "current_patient" not in st.session_state:
    st.session_state.current_patient = None

# =========================================================
# MODE
# =========================================================
mode = st.sidebar.selectbox(
    "Mode ICU",
    ["ICU FLOW", "QUICK ICU", "PERFUSION ICU REAL", "PERFUSION TERRAIN", "IA CLINIQUE"]
)

# =========================================================
# PATIENT MANAGEMENT
# =========================================================
st.sidebar.markdown("## 🧠 ICU FLOW")

new_patient = st.sidebar.text_input("Créer patient")

if st.sidebar.button("➕ Ajouter patient") and new_patient.strip():
    st.session_state.patients[new_patient] = {
        "cibles": {
            "hemodynamique": [],
            "respiratoire": [],
            "neuro": [],
            "renal": [],
            "infectieux": []
        },
        "notes": []
    }
    st.session_state.current_patient = new_patient
    st.success(f"Patient créé : {new_patient}")

patient_list = list(st.session_state.patients.keys())

if patient_list:
    selected = st.sidebar.selectbox(
        "Patient actif",
        patient_list,
        index=patient_list.index(st.session_state.current_patient)
        if st.session_state.current_patient in patient_list else 0
    )
    st.session_state.current_patient = selected

# =========================================================
# RESET
# =========================================================
if st.sidebar.button("Reset session"):
    st.session_state.messages = []
    st.rerun()

# =========================================================
# HISTORY
# =========================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# INPUT
# =========================================================
user_input = st.chat_input("Entrée ICU...")

# =========================================================
# CLINICAL ENGINE
# =========================================================
def extract_clinical(text):
    t = text.lower()
    data = {
        "hemodynamique": [],
        "respiratoire": [],
        "neuro": [],
        "renal": [],
        "infectieux": []
    }

    if "norad" in t or "nora" in t:
        data["hemodynamique"].append("noradrénaline en cours")
    if "hypotension" in t or "map" in t:
        data["hemodynamique"].append("instabilité tensionnelle")

    if "ventil" in t or "intub" in t or "peep" in t:
        data["respiratoire"].append("ventilation mécanique")

    if "propof" in t:
        data["neuro"].append("propofol")
    if "midaz" in t:
        data["neuro"].append("midazolam")
    if "agitation" in t:
        data["neuro"].append("agitation")

    if "creat" in t or "diurese" in t or "oligurie" in t:
        data["renal"].append("fonction rénale à surveiller")

    if "sepsis" in t or "infection" in t:
        data["infectieux"].append("sepsis suspect")
    if "fièvre" in t or "38" in t:
        data["infectieux"].append("syndrome fébrile")

    return data


def compute_score(text, cibles):
    t = text.lower()
    score = 0

    hemo = " ".join(cibles.get("hemodynamique", [])).lower()
    if "norad" in t or "noradrénaline" in hemo:
        score += 3
    if "hypotension" in t or "instabilité" in hemo:
        score += 3
    if "sepsis" in t or "sepsis" in " ".join(cibles.get("infectieux", [])).lower():
        score += 3
    if "ventil" in t or "intub" in t or "ventilation" in " ".join(cibles.get("respiratoire", [])).lower():
        score += 2
    if "propof" in t or "midaz" in t or any(x in " ".join(cibles.get("neuro", [])).lower() for x in ["propofol", "midazolam"]):
        score += 1
    if "creat" in t or "diurese" in t or "oligurie" in t or "rénale" in " ".join(cibles.get("renal", [])).lower():
        score += 1

    if score >= 6:
        label = "🔴 CRITIQUE"
    elif score >= 3:
        label = "🟠 INSTABLE"
    else:
        label = "🟢 STABLE"

    return score, label


def build_triage(text, cibles):
    t = text.lower()
    urgent = []
    important = []
    surveillance = []

    hemo = " ".join(cibles.get("hemodynamique", [])).lower()
    resp = " ".join(cibles.get("respiratoire", [])).lower()
    neuro = " ".join(cibles.get("neuro", [])).lower()
    renal = " ".join(cibles.get("renal", [])).lower()
    infect = " ".join(cibles.get("infectieux", [])).lower()

    # URGENT
    if "norad" in t or "noradrénaline" in hemo:
        urgent.append("🫀 Noradrénaline active — instabilité hémodynamique")
    if "hypotension" in t or "instabilité" in hemo:
        urgent.append("🫀 Hypotension / MAP critique")
    if "sepsis" in t or "sepsis" in infect:
        urgent.append("🦠 Sepsis — foyer infectieux actif")
    if "intub" in t:
        urgent.append("🫁 Patient intubé — ventilation invasive")

    # IMPORTANT
    if ("ventil" in t or "peep" in t or "ventilation" in resp) and "intub" not in t:
        important.append("🫁 Ventilation mécanique en cours")
    if "propof" in t or "propofol" in neuro:
        important.append("🧠 Sédation propofol — réévaluation profondeur")
    if "midaz" in t or "midazolam" in neuro:
        important.append("🧠 Sédation midazolam — réévaluation profondeur")
    if "fièvre" in t or "38" in t or "fébrile" in infect:
        important.append("🌡️ Syndrome fébrile — bilan infectieux")
    if "creat" in t or "diurese" in t or "oligurie" in t or "rénale" in renal:
        important.append("🧪 Fonction rénale altérée / oligurie")

    # SURVEILLANCE
    if "agitation" in t or "agitation" in neuro:
        surveillance.append("🧠 Agitation — monitoring neurologique")
    if not urgent and not important:
        surveillance.append("✅ Paramètres stables — surveillance standard")

    return urgent, important, surveillance


def build_actions(text, cibles):
    t = text.lower()
    actions = []

    hemo = " ".join(cibles.get("hemodynamique", [])).lower()
    infect = " ".join(cibles.get("infectieux", [])).lower()
    resp = " ".join(cibles.get("respiratoire", [])).lower()
    neuro = " ".join(cibles.get("neuro", [])).lower()
    renal = " ".join(cibles.get("renal", [])).lower()

    if "norad" in t or "noradrénaline" in hemo:
        actions.append("Titration noradrénaline → cible MAP ≥ 65 mmHg")
    if "hypotension" in t or "instabilité" in hemo:
        actions.append("Surveillance tensionnelle rapprochée + remplissage si hypovolémie")
    if "sepsis" in t or "sepsis" in infect:
        actions.append("Hémocultures × 2 + antibiothérapie probabiliste dans l'heure")
    if "ventil" in t or "intub" in t or "peep" in t or "ventilation" in resp:
        actions.append("Vérification paramètres ventilatoires — FiO2 / PEEP / Vt")
    if "propof" in t or "propofol" in neuro or "midaz" in t or "midazolam" in neuro:
        actions.append("Réévaluation sédation — score RASS / adaptation doses")
    if "creat" in t or "diurese" in t or "oligurie" in t or "rénale" in renal:
        actions.append("Bilan rénal : créatinine + diurèse horaire")
    if "fièvre" in t or "38" in t:
        actions.append("Bilan infectieux complet — NFS / CRP / hémocultures")

    return actions


def format_flow_answer(score, label, urgent, important, surveillance, actions):
    def fmt(lst, icon):
        if not lst:
            return f"{icon} aucun élément\n"
        return "\n".join(f"- {x}" for x in lst) + "\n"

    act_str = "\n".join(f"- {a}" for a in actions) if actions else "- aucune action requise"

    return f"""
⚠️ SCORE PATIENT : {score} — {label}

━━━━━━━━━━━━━━━━━━

🔴 URGENT
{fmt(urgent, "🔴")}
🟠 IMPORTANT
{fmt(important, "🟠")}
🟢 SURVEILLANCE
{fmt(surveillance, "🟢")}
━━━━━━━━━━━━━━━━━━

⚡ ACTIONS IMMÉDIATES
{act_str}

👉 ICU ENGINE ACTIVE
"""

# =========================================================
# FLOW MODE
# =========================================================
if mode == "ICU FLOW":

    if user_input:

        if not st.session_state.current_patient:
            st.warning("⚠️ Aucun patient sélectionné")
            st.stop()

        patient = st.session_state.patients[st.session_state.current_patient]
        extracted = extract_clinical(user_input)

        # MEMORY UPDATE
        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]:
                    patient["cibles"][k].append(item)

        if not any(extracted.values()):
            patient["notes"].append(user_input)

        score, label = compute_score(user_input, patient["cibles"])
        urgent, important, surveillance = build_triage(user_input, patient["cibles"])
        actions = build_actions(user_input, patient["cibles"])
        answer = format_flow_answer(score, label, urgent, important, surveillance, actions)

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# =========================================================
# CLASSIC MODES
# =========================================================
else:

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        context = search_icu(user_input)

        if mode == "QUICK ICU":
            answer = f"⚡ QUICK ICU\n\n{context or 'non documenté'}"
        elif mode == "PERFUSION ICU REAL":
            answer = "💉 PERFUSION ICU REAL"
        elif mode == "PERFUSION TERRAIN":
            answer = "🏥 PERFUSION TERRAIN"
        else:
            answer = f"🧠 IA ICU\n\n{user_input}\n\n{context}"

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
