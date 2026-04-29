import streamlit as st
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V9.5", page_icon="🏥", layout="wide")

# =========================================================
# HEADER
# =========================================================
st.title("🏥 ICU ENGINE V9.5")
st.caption("ICU FLOW decision support - monitor mode")

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
# CLINICAL ENGINE V9.5 + PAM
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

    if "norad" in t or "nora" in t or "vasopresseur" in t:
        data["hemodynamique"].append("noradrénaline")
    if "hypotension" in t or "map" in t or "instabilité" in t or "pam" in t:
        data["hemodynamique"].append("instabilité tensionnelle")
    if "choc" in t:
        data["hemodynamique"].append("choc")

    if "ventil" in t or "intub" in t or "peep" in t or "fio2" in t:
        data["respiratoire"].append("ventilation mécanique")
    if "hypoxém" in t or "spo2" in t or "crépitant" in t:
        data["respiratoire"].append("hypoxémie")

    if "propof" in t:
        data["neuro"].append("propofol")
    if "midaz" in t:
        data["neuro"].append("midazolam")
    if "agitation" in t:
        data["neuro"].append("agitation")
    if "sédation" in t or "sedation" in t:
        data["neuro"].append("sédation")

    if "creat" in t or "diurese" in t or "oligurie" in t or "diurèse" in t:
        data["renal"].append("insuffisance rénale")

    if "sepsis" in t or "choc septique" in t:
        data["infectieux"].append("sepsis")
    if "infection" in t or "infectieux" in t or "antibio" in t:
        data["infectieux"].append("infection active")
    if "fièvre" in t or "38" in t or "39" in t or "hémoculture" in t:
        data["infectieux"].append("foyer infectieux")

    return data


# =========================================================
# PAM DETECTION
# =========================================================
def detect_pam_risk(text, flags):
    """
    Retourne le niveau PAM estimé :
    - "basse"   : hypoperfusion probable, cible non atteinte
    - "limite"  : zone limite, surveillance requise
    - "correcte": PAM probablement ≥ 65 mmHg
    - None      : pas d'élément hémodynamique détecté
    """
    t = text.lower()

    # PAM explicitement mentionnée avec valeur basse
    import re
    pam_values = re.findall(r'(?:map|pam)[^\d]*(\d{2,3})', t)
    if pam_values:
        vals = [int(v) for v in pam_values]
        min_val = min(vals)
        if min_val < 60:
            return "basse"
        elif min_val < 65:
            return "limite"
        else:
            return "correcte"

    # Déduction contextuelle
    triggers_basse = [
        flags["choc"],
        flags["vasopresseur"] and flags["hypotension"],
        "hypotension sévère" in t,
        "map insuffisante" in t,
        "pam basse" in t,
    ]
    triggers_limite = [
        flags["vasopresseur"] and not flags["hypotension"],
        flags["hypotension"] and not flags["vasopresseur"],
        "fluctuante" in t,
        "map entre" in t,
    ]

    if any(triggers_basse):
        return "basse"
    if any(triggers_limite):
        return "limite"
    if flags["vasopresseur"] or flags["hypotension"] or flags["choc"]:
        return "limite"

    return None


def compute_flags(text, cibles):
    t = text.lower()
    all_data = " ".join(" ".join(v) for v in cibles.values()).lower()

    flags = {
        "vasopresseur": "noradrénaline" in all_data or "norad" in t or "vasopresseur" in t,
        "hypotension": "instabilité tensionnelle" in all_data or "hypotension" in t or "map" in t or "pam" in t,
        "choc": "choc" in all_data or "choc" in t,
        "sepsis": "sepsis" in all_data or "sepsis" in t,
        "infection": "infection" in all_data or "antibio" in t or "hémoculture" in t,
        "ventilation": "ventilation mécanique" in all_data or "ventil" in t or "intub" in t,
        "hypoxemie": "hypoxémie" in all_data or "hypoxém" in t or "fio2" in t or "crépitant" in t,
        "sedation": any(x in all_data for x in ["propofol", "midazolam", "sédation"]),
        "renal": "insuffisance rénale" in all_data or "creat" in t or "oligurie" in t or "diurèse" in t,
        "agitation": "agitation" in all_data,
        "aggravation": any(x in t for x in [
            "aggrav", "progression", "dégradation", "fluctuante",
            "persistante", "sévère", "positives"
        ])
    }
    return flags


def build_verdict(flags, pam_level):
    if flags["choc"] and flags["sepsis"]:
        pam_str = " — PAM cible non atteinte" if pam_level in ("basse", "limite") else ""
        return f"Patient critique — choc septique actif avec instabilité hémodynamique sous vasopresseurs{pam_str}"
    if flags["vasopresseur"] and flags["hypotension"]:
        return "Patient critique instable — dépendance vasopressive élevée, PAM insuffisante"
    if flags["sepsis"] and flags["ventilation"]:
        return "Patient instable — sepsis sévère sous ventilation invasive"
    if flags["vasopresseur"]:
        pam_str = " / PAM limite" if pam_level == "limite" else ""
        return f"État instable sous vasopresseurs{pam_str} — surveillance hémodynamique rapprochée requise"
    if flags["ventilation"] and flags["hypoxemie"]:
        return "Patient instable — hypoxémie persistante malgré ventilation optimisée"
    return "Patient en surveillance — paramètres à réévaluer"


def build_monitor_alerts(flags, pam_level):
    critique = []
    important = []
    surveillance = []

    # CRITIQUE
    if flags["choc"] and flags["sepsis"]:
        critique.append("choc septique / instabilité hémodynamique")
    elif flags["vasopresseur"] and flags["hypotension"]:
        critique.append("vasopresseurs actifs / MAP insuffisante")
    elif flags["vasopresseur"]:
        critique.append("dépendance vasopressive")

    # PAM → CRITIQUE si basse, IMPORTANT si limite
    if pam_level == "basse":
        critique.append("hypoperfusion d'organe (PAM < 65 mmHg suspectée)")
    elif pam_level == "limite":
        important.append("PAM limite / cible ≥ 65 mmHg non assurée")

    if flags["hypoxemie"] and flags["ventilation"]:
        critique.append("hypoxémie réfractaire sous VM")
    elif flags["ventilation"]:
        critique.append("ventilation invasive active")

    if flags["sepsis"] and flags["infection"]:
        critique.append("sepsis — foyer non contrôlé")

    # IMPORTANT
    if flags["sedation"]:
        important.append("sédation profonde / risque hypotension")
    if flags["renal"]:
        important.append("oligurie / insuffisance rénale progressive")
    if flags["infection"] and not flags["sepsis"]:
        important.append("infection active / bilan en cours")
    if flags["hypoxemie"] and not flags["ventilation"]:
        important.append("hypoxémie / oxygénothérapie à adapter")

    # SURVEILLANCE
    if flags["agitation"]:
        surveillance.append("agitation résiduelle / monitoring neuro")
    if not critique and not important:
        surveillance.append("paramètres stables — monitoring standard")

    return critique, important, surveillance


def build_evolution(flags, pam_level):
    score = 0
    if flags["choc"]:
        score += 3
    if flags["sepsis"]:
        score += 2
    if flags["vasopresseur"] and flags["hypotension"]:
        score += 2
    if flags["aggravation"]:
        score += 2
    if flags["hypoxemie"]:
        score += 1
    if flags["renal"]:
        score += 1
    if pam_level == "basse":
        score += 2
    elif pam_level == "limite":
        score += 1

    if score >= 7:
        return "🔴 AGGRAVATION"
    elif score >= 4:
        return "🟠 DÉGRADATION"
    elif score >= 2:
        return "🟡 INDÉTERMINÉ"
    else:
        return "🟢 STABLE"


def build_actions(flags, pam_level):
    actions = []

    # PAM en tête si instable
    if pam_level in ("basse", "limite"):
        actions.append("Titration vasopresseur → objectif PAM ≥ 65 mmHg")
        if flags["choc"] or flags["hypotension"]:
            actions.append("Optimisation volémie — remplissage si précharge-dépendant")
    elif flags["vasopresseur"] or flags["hypotension"]:
        actions.append("Titration noradrénaline → cible MAP ≥ 65 mmHg")

    if flags["choc"] and flags["sepsis"]:
        actions.append("Lactate de contrôle + réévaluation remplissage")
    if flags["sepsis"] or flags["infection"]:
        actions.append("Hémocultures (si non faites) + antibiothérapie dans l'heure")
    if flags["ventilation"] or flags["hypoxemie"]:
        actions.append("Optimisation ventilatoire — FiO2 / PEEP / plateau")
    if flags["sedation"]:
        actions.append("Réévaluation sédation — score RASS + adaptation doses")
    if flags["renal"]:
        actions.append("Surveillance diurèse horaire + créatinine de contrôle")

    return actions


def format_v95(verdict, critique, important, surveillance, evolution, actions):

    def fmt_alerts(lst, icon):
        if not lst:
            return f"  {icon} aucun\n"
        return "\n".join(f"  {icon} {x}" for x in lst) + "\n"

    act_str = "\n".join(f"  — {a}" for a in actions) if actions else "  — aucune action requise"

    return f"""
🚨 VERDICT CLINIQUE
{verdict}

━━━━━━━━━━━━━━━━━━

📊 ALERTES MONITOR ICU

🔴 CRITIQUE
{fmt_alerts(critique, "🔴")}
🟠 IMPORTANT
{fmt_alerts(important, "🟠")}
🟢 SURVEILLANCE
{fmt_alerts(surveillance, "🟢")}
━━━━━━━━━━━━━━━━━━

📈 ÉVOLUTION : {evolution}

━━━━━━━━━━━━━━━━━━

⚡ ACTIONS IMMÉDIATES
{act_str}

👉 ICU ENGINE V9.5
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

        flags = compute_flags(user_input, patient["cibles"])
        pam_level = detect_pam_risk(user_input, flags)
        verdict = build_verdict(flags, pam_level)
        critique, important, surveillance = build_monitor_alerts(flags, pam_level)
        evolution = build_evolution(flags, pam_level)
        actions = build_actions(flags, pam_level)
        answer = format_v95(verdict, critique, important, surveillance, evolution, actions)

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
