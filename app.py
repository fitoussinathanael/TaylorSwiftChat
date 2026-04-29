import streamlit as st
import re
from rag_icu import search_icu

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="ICU Engine V10.1", page_icon="🏥", layout="wide")

# =========================================================
# HEADER
# =========================================================
st.title("🏥 ICU ENGINE V10.1")
st.caption("ICU FLOW decision support - final stable")

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
        "numerics": {
            "pam": [],
            "norad": [],
            "fio2": [],
            "pf_ratio": [],
            "diurese": [],
            "creatinine": [],
            "lactate": [],
            "temperature": [],
            "spo2": []
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
# NUMERIC EXTRACTOR
# =========================================================
def extract_numerics(text):
    t = text.lower()
    found = {}

    pam = re.findall(r'(?:map|pam)[^\d]*(\d{2,3})', t)
    if pam:
        found["pam"] = int(pam[-1])
    pam_range = re.findall(r'entre\s+(\d{2,3})\s+et\s+(\d{2,3})\s*(?:mmhg)?', t)
    if pam_range and "pam" not in found:
        found["pam"] = int(pam_range[-1][0])

    norad = re.findall(r'(?:norad|nora|noradrénaline)[^\d]*(\d+[.,]\d+)', t)
    if norad:
        found["norad"] = float(norad[-1].replace(",", "."))

    fio2 = re.findall(r'fio2\s*[:\-]?\s*(\d{2,3})\s*%?', t)
    if fio2:
        found["fio2"] = int(fio2[-1])

    spo2 = re.findall(r'spo2\s*[:\-]?\s*(\d{2,3})\s*%?', t)
    if spo2:
        found["spo2"] = int(spo2[-1])

    pf = re.findall(r'(?:p/f|pf|rapport\s*p/?f)[^\d]*(\d{2,3})', t)
    if pf:
        found["pf_ratio"] = int(pf[-1])

    diurese = re.findall(r'(?:diur[eèé]se)[^\d]*(\d+[.,]?\d*)\s*(?:ml/kg|ml)', t)
    if diurese:
        found["diurese"] = float(diurese[-1].replace(",", "."))
    diurese2 = re.findall(r'(\d+[.,]\d+)\s*ml/kg/h', t)
    if diurese2 and "diurese" not in found:
        found["diurese"] = float(diurese2[-1].replace(",", "."))

    creat = re.findall(r'cr[eé]atinine[^\d]*(\d{2,4})', t)
    if creat:
        found["creatinine"] = int(creat[-1])

    lactate = re.findall(r'lactat[e]?[^\d]*(\d+[.,]\d+)', t)
    if lactate:
        found["lactate"] = float(lactate[-1].replace(",", "."))

    temp = re.findall(r'(?:fièvre|température|temp)[^\d]*(\d{2}[.,]\d)', t)
    if temp:
        found["temperature"] = float(temp[-1].replace(",", "."))
    temp2 = re.findall(r'(\d{2}[.,]\d)\s*°c', t)
    if temp2 and "temperature" not in found:
        found["temperature"] = float(temp2[-1].replace(",", "."))

    return found


def update_numerics(patient, new_vals):
    for k, v in new_vals.items():
        if k in patient["numerics"]:
            patient["numerics"][k].append(v)
            patient["numerics"][k] = patient["numerics"][k][-5:]


def get_last(patient, key):
    vals = patient["numerics"].get(key, [])
    return vals[-1] if vals else None


def analyze_numerics(patient):
    analysis = {}

    pam = get_last(patient, "pam")
    if pam is not None:
        if pam < 60:
            analysis["pam"] = ("critique", f"PAM {pam} mmHg")
        elif pam < 65:
            analysis["pam"] = ("limite", f"PAM {pam} mmHg")
        else:
            analysis["pam"] = ("ok", f"PAM {pam} mmHg")

    norad = get_last(patient, "norad")
    if norad is not None:
        if norad >= 0.5:
            analysis["norad"] = ("critique", f"Norad {norad} µg/kg/min")
        elif norad >= 0.25:
            analysis["norad"] = ("limite", f"Norad {norad} µg/kg/min")
        else:
            analysis["norad"] = ("ok", f"Norad {norad} µg/kg/min")

    pf = get_last(patient, "pf_ratio")
    fio2 = get_last(patient, "fio2")
    if pf is not None:
        if pf < 100:
            analysis["respiratoire"] = ("critique", f"P/F {pf}")
        elif pf < 200:
            analysis["respiratoire"] = ("limite", f"P/F {pf}")
        elif pf < 300:
            analysis["respiratoire"] = ("surveillance", f"P/F {pf}")
        else:
            analysis["respiratoire"] = ("ok", f"P/F {pf}")
    elif fio2 is not None:
        if fio2 >= 80:
            analysis["respiratoire"] = ("critique", f"FiO2 {fio2}%")
        elif fio2 >= 60:
            analysis["respiratoire"] = ("limite", f"FiO2 {fio2}%")
        else:
            analysis["respiratoire"] = ("ok", f"FiO2 {fio2}%")

    diurese = get_last(patient, "diurese")
    if diurese is not None:
        if diurese < 0.3:
            analysis["diurese"] = ("critique", f"Diurèse {diurese} mL/kg/h")
        elif diurese < 0.5:
            analysis["diurese"] = ("limite", f"Diurèse {diurese} mL/kg/h")
        else:
            analysis["diurese"] = ("ok", f"Diurèse {diurese} mL/kg/h")

    creat = get_last(patient, "creatinine")
    if creat is not None:
        if creat > 300:
            analysis["creatinine"] = ("critique", f"Créatinine {creat} µmol/L")
        elif creat > 150:
            analysis["creatinine"] = ("limite", f"Créatinine {creat} µmol/L")
        else:
            analysis["creatinine"] = ("ok", f"Créatinine {creat} µmol/L")

    lactate = get_last(patient, "lactate")
    if lactate is not None:
        if lactate >= 4:
            analysis["lactate"] = ("critique", f"Lactate {lactate} mmol/L")
        elif lactate >= 2:
            analysis["lactate"] = ("limite", f"Lactate {lactate} mmol/L")
        else:
            analysis["lactate"] = ("ok", f"Lactate {lactate} mmol/L")

    temp = get_last(patient, "temperature")
    if temp is not None:
        if temp >= 39.5:
            analysis["temperature"] = ("critique", f"T° {temp}°C")
        elif temp >= 38.5:
            analysis["temperature"] = ("limite", f"T° {temp}°C")
        else:
            analysis["temperature"] = ("ok", f"T° {temp}°C")

    return analysis


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


def compute_flags(text, cibles):
    t = text.lower()
    all_data = " ".join(" ".join(v) for v in cibles.values()).lower()

    return {
        "vasopresseur": "noradrénaline" in all_data or "norad" in t or "vasopresseur" in t,
        "hypotension":  "instabilité tensionnelle" in all_data or "hypotension" in t or "map" in t or "pam" in t,
        "choc":         "choc" in all_data or "choc" in t,
        "sepsis":       "sepsis" in all_data or "sepsis" in t,
        "infection":    "infection" in all_data or "antibio" in t or "hémoculture" in t,
        "ventilation":  "ventilation mécanique" in all_data or "ventil" in t or "intub" in t,
        "hypoxemie":    "hypoxémie" in all_data or "hypoxém" in t or "fio2" in t or "crépitant" in t,
        "sedation":     any(x in all_data for x in ["propofol", "midazolam", "sédation"]),
        "renal":        "insuffisance rénale" in all_data or "creat" in t or "oligurie" in t or "diurèse" in t,
        "agitation":    "agitation" in all_data,
        "aggravation":  any(x in t for x in [
            "aggrav", "progression", "dégradation", "fluctuante",
            "persistante", "sévère", "positives"
        ])
    }


def detect_pam_risk(text, flags, num_analysis):
    if "pam" in num_analysis:
        level, _ = num_analysis["pam"]
        return {"critique": "basse", "limite": "limite"}.get(level, "correcte")

    t = text.lower()
    if any([flags["choc"] and flags["vasopresseur"],
            flags["vasopresseur"] and flags["hypotension"],
            "hypotension sévère" in t]):
        return "basse"
    if any([flags["vasopresseur"] and not flags["hypotension"],
            flags["hypotension"] and not flags["vasopresseur"],
            "fluctuante" in t]):
        return "limite"
    if flags["vasopresseur"] or flags["hypotension"] or flags["choc"]:
        return "limite"
    return None


# =========================================================
# V10.1 — PROBLÈME PRINCIPAL + FUSION ALERTES
# =========================================================
def build_main_problem(flags, pam_level, num_analysis):
    """
    Identifie LE problème principal unique du patient.
    1 phrase. Physiopathologie dominante uniquement.
    """
    norad = num_analysis.get("norad")
    norad_str = f" sous norad {norad[1].split()[1]} µg/kg/min" if norad else ""

    # Priorité 1 : choc septique avec vasopresseurs
    if flags["choc"] and flags["sepsis"] and flags["vasopresseur"]:
        pam = num_analysis.get("pam")
        pam_str = f" — {pam[1]}" if pam else ""
        return f"Choc septique vasoplégique{norad_str}{pam_str}"

    # Priorité 2 : sepsis sans choc constitué mais vasopresseurs
    if flags["sepsis"] and flags["vasopresseur"]:
        return f"Sepsis sévère avec dépendance vasopressive{norad_str}"

    # Priorité 3 : défaillance respiratoire dominante
    resp = num_analysis.get("respiratoire")
    if flags["hypoxemie"] and flags["ventilation"] and not flags["vasopresseur"]:
        resp_str = f" — {resp[1]}" if resp else ""
        return f"Défaillance respiratoire sous ventilation invasive{resp_str}"

    # Priorité 4 : instabilité hémodynamique non septique
    if flags["vasopresseur"] and flags["hypotension"]:
        return f"Instabilité hémodynamique sous vasopresseurs{norad_str}"

    # Priorité 5 : défaillance multi-organe
    organ_count = sum([
        flags["vasopresseur"],
        flags["hypoxemie"] or flags["ventilation"],
        flags["renal"]
    ])
    if organ_count >= 2:
        return "Défaillance multi-organe en cours — surveillance rapprochée"

    # Défaut
    return "Patient instable — évaluation multi-systémique requise"


def build_action_prioritaire(flags, pam_level, num_analysis):
    """
    Action numéro 1 absolue. 1 ligne. Si tu ne fais qu'une chose.
    """
    pam = num_analysis.get("pam")
    norad = num_analysis.get("norad")

    if flags["choc"] and flags["sepsis"]:
        if pam_level in ("basse", "limite"):
            pam_str = f"({pam[1]} → cible ≥ 65)" if pam else "(cible ≥ 65 mmHg)"
            return f"Titrer noradrénaline {pam_str} + antibiothérapie si non débutée"
        return "Antibiothérapie probabiliste immédiate + contrôle hémodynamique"

    if pam_level == "basse":
        pam_str = f"({pam[1]})" if pam else ""
        return f"Titration vasopresseur urgente {pam_str} — objectif PAM ≥ 65 mmHg"

    if flags["hypoxemie"] and flags["ventilation"]:
        resp = num_analysis.get("respiratoire")
        resp_str = f"({resp[1]})" if resp else ""
        return f"Optimisation ventilatoire {resp_str} — adapter FiO2 / PEEP"

    if flags["sepsis"] and flags["infection"]:
        return "Hémocultures + antibiothérapie probabiliste dans l'heure"

    if pam_level == "limite":
        return "Surveillance MAP continue — titrer si < 65 mmHg"

    if flags["renal"]:
        return "Surveillance diurèse horaire stricte + bilan rénal"

    return "Réévaluation clinique complète — paramètres à stabiliser"


def build_monitor_alerts_fused(flags, pam_level, num_analysis):
    """
    Alertes fusionnées par cluster physiopathologique.
    Maximum 2 items rouges, 2 oranges, 1 vert.
    Pas de doublon organe/symptôme.
    """
    critique = []
    important = []
    surveillance = []

    pam = num_analysis.get("pam")
    norad = num_analysis.get("norad")
    resp = num_analysis.get("respiratoire")
    diurese = num_analysis.get("diurese")
    creat = num_analysis.get("creatinine")
    lactate = num_analysis.get("lactate")
    temp = num_analysis.get("temperature")

    # ── CLUSTER 1 : hémodynamique (1 seule alerte fusionnée) ──
    if flags["vasopresseur"] or flags["choc"] or pam_level in ("basse", "limite"):
        parts = []
        if flags["choc"] and flags["sepsis"]:
            parts.append("choc septique")
        elif flags["vasopresseur"]:
            parts.append("vasopresseurs actifs")
        if norad:
            parts.append(norad[1])
        if pam:
            parts.append(pam[1])
        elif pam_level == "basse":
            parts.append("PAM < 65 mmHg")
        elif pam_level == "limite":
            parts.append("PAM limite")
        label = " / ".join(parts) if parts else "instabilité hémodynamique"
        if pam_level == "basse" or (flags["choc"] and flags["sepsis"]):
            critique.append(f"🫀 {label}")
        else:
            important.append(f"🫀 {label}")

    # ── CLUSTER 2 : respiratoire (1 seule alerte fusionnée) ──
    if flags["ventilation"] or flags["hypoxemie"]:
        parts = []
        if flags["ventilation"]:
            parts.append("VM invasive")
        if flags["hypoxemie"]:
            parts.append("hypoxémie")
        if resp:
            parts.append(resp[1])
        label = " / ".join(parts)
        if resp and resp[0] == "critique":
            critique.append(f"🫁 {label}")
        else:
            important.append(f"🫁 {label}")

    # ── CLUSTER 3 : infectieux (1 seule alerte fusionnée) ──
    if flags["sepsis"] or flags["infection"]:
        parts = []
        if flags["sepsis"]:
            parts.append("sepsis actif")
        elif flags["infection"]:
            parts.append("infection en cours")
        if temp and temp[0] in ("critique", "limite"):
            parts.append(temp[1])
        label = " / ".join(parts)
        if flags["sepsis"]:
            critique.append(f"🦠 {label}")
        else:
            important.append(f"🦠 {label}")

    # ── CLUSTER 4 : rénal (important ou surveillance) ──
    if flags["renal"] or diurese or creat:
        parts = []
        if diurese and diurese[0] in ("critique", "limite"):
            parts.append(diurese[1])
        if creat and creat[0] in ("critique", "limite"):
            parts.append(creat[1])
        label = " / ".join(parts) if parts else "fonction rénale altérée"
        if (diurese and diurese[0] == "critique") or (creat and creat[0] == "critique"):
            important.append(f"🧪 {label}")
        else:
            surveillance.append(f"🧪 {label}")

    # ── CLUSTER 5 : sédation ──
    if flags["sedation"]:
        important.append("🧠 sédation IV — réévaluation RASS")

    # ── CLUSTER 6 : lactate ──
    if lactate and lactate[0] in ("critique", "limite"):
        important.append(f"🩸 {lactate[1]} — hypoperfusion tissulaire")

    # ── SURVEILLANCE générale ──
    if flags["agitation"]:
        surveillance.append("🧠 agitation résiduelle")
    if not critique and not important:
        surveillance.append("✅ paramètres stables — monitoring standard")

    # Limite visuelle : max 3 rouges, 3 oranges
    critique = critique[:3]
    important = important[:3]

    return critique, important, surveillance


def build_evolution(flags, pam_level, num_analysis):
    score = 0
    if flags["choc"]:         score += 3
    if flags["sepsis"]:       score += 2
    if flags["vasopresseur"] and flags["hypotension"]: score += 2
    if flags["aggravation"]:  score += 2
    if flags["hypoxemie"]:    score += 1
    if flags["renal"]:        score += 1
    if pam_level == "basse":  score += 2
    elif pam_level == "limite": score += 1

    norad = num_analysis.get("norad")
    if norad and norad[0] == "critique":   score += 2
    elif norad and norad[0] == "limite":   score += 1

    resp = num_analysis.get("respiratoire")
    if resp and resp[0] == "critique":     score += 2
    elif resp and resp[0] == "limite":     score += 1

    lactate = num_analysis.get("lactate")
    if lactate and lactate[0] == "critique": score += 2
    elif lactate and lactate[0] == "limite": score += 1

    if score >= 7:   return "🔴 AGGRAVATION"
    elif score >= 4: return "🟠 DÉGRADATION"
    elif score >= 2: return "🟡 INDÉTERMINÉ"
    else:            return "🟢 STABLE"


def build_actions_v101(flags, pam_level, num_analysis):
    """
    Actions secondaires uniquement — l'action prioritaire est déjà affichée séparément.
    Max 4 lignes, courtes, terrain.
    """
    actions = []
    pam = num_analysis.get("pam")
    norad = num_analysis.get("norad")
    resp = num_analysis.get("respiratoire")
    diurese = num_analysis.get("diurese")
    creat = num_analysis.get("creatinine")
    lactate = num_analysis.get("lactate")

    # Hémodynamique secondaire
    if flags["choc"] and flags["sepsis"]:
        lac_str = f"— {lactate[1]}" if lactate else ""
        actions.append(f"Lactate de contrôle {lac_str} + réévaluation remplissage".strip())
    elif pam_level in ("basse", "limite") and not (flags["choc"] and flags["sepsis"]):
        actions.append("Optimisation volémie si précharge-dépendant")

    # Infectieux secondaire
    if flags["sepsis"] or flags["infection"]:
        actions.append("Réévaluation antibiothérapie — résultats hémocultures")

    # Respiratoire secondaire
    if flags["ventilation"] or flags["hypoxemie"]:
        resp_str = f"({resp[1]})" if resp else ""
        actions.append(f"Contrôle gazométrique + paramètres VM {resp_str}".strip())

    # Sédation
    if flags["sedation"]:
        actions.append("Score RASS — adapter sédation si stable hémodynamique")

    # Rénal
    if flags["renal"] or diurese or creat:
        parts = []
        if diurese:
            parts.append(diurese[1])
        if creat:
            parts.append(creat[1])
        label = " / ".join(parts) if parts else "diurèse + créatinine"
        actions.append(f"Surveillance rénale — {label}")

    return actions[:4]


def build_numeric_panel(patient, num_analysis):
    lines = []
    order = [
        ("pam",          "🫀 PAM"),
        ("norad",        "💉 Norad"),
        ("respiratoire", "🫁 Respi"),
        ("diurese",      "🧪 Diurèse"),
        ("creatinine",   "🧪 Créat"),
        ("lactate",      "🩸 Lactate"),
        ("temperature",  "🌡️ Temp"),
    ]
    icons = {"critique": "🔴", "limite": "🟠", "ok": "🟢", "surveillance": "🟡"}

    for key, label in order:
        val = num_analysis.get(key)
        if val:
            level, desc = val
            icon = icons.get(level, "⚪")
            lines.append(f"{icon} {label} : {desc}")

    return "\n".join(lines) if lines else "  aucune valeur chiffrée détectée"


def format_v101(main_problem, action_prio, critique, important,
                surveillance, evolution, actions, numeric_panel):

    def fmt(lst):
        if not lst:
            return "  aucun\n"
        return "\n".join(f"  {x}" for x in lst) + "\n"

    act_str = "\n".join(f"  — {a}" for a in actions) if actions else "  — aucune action secondaire"

    return f"""
🎯 PROBLÈME PRINCIPAL
{main_problem}

━━━━━━━━━━━━━━━━━━

⚡ ACTION PRIORITAIRE
{action_prio}

━━━━━━━━━━━━━━━━━━

📊 ALERTES MONITOR ICU

🔴 CRITIQUE
{fmt(critique)}
🟠 IMPORTANT
{fmt(important)}
🟢 SURVEILLANCE
{fmt(surveillance)}
━━━━━━━━━━━━━━━━━━

📈 ÉVOLUTION : {evolution}

━━━━━━━━━━━━━━━━━━

🔢 VALEURS CLÉS
{numeric_panel}

━━━━━━━━━━━━━━━━━━

📋 ACTIONS SECONDAIRES
{act_str}

👉 ICU ENGINE V10.1
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

        for k in extracted:
            for item in extracted[k]:
                if item not in patient["cibles"][k]:
                    patient["cibles"][k].append(item)

        if not any(extracted.values()):
            patient["notes"].append(user_input)

        new_numerics = extract_numerics(user_input)
        update_numerics(patient, new_numerics)

        flags        = compute_flags(user_input, patient["cibles"])
        num_analysis = analyze_numerics(patient)
        pam_level    = detect_pam_risk(user_input, flags, num_analysis)

        main_problem  = build_main_problem(flags, pam_level, num_analysis)
        action_prio   = build_action_prioritaire(flags, pam_level, num_analysis)
        critique, important, surveillance = build_monitor_alerts_fused(flags, pam_level, num_analysis)
        evolution     = build_evolution(flags, pam_level, num_analysis)
        actions       = build_actions_v101(flags, pam_level, num_analysis)
        numeric_panel = build_numeric_panel(patient, num_analysis)

        answer = format_v101(
            main_problem, action_prio,
            critique, important, surveillance,
            evolution, actions, numeric_panel
        )

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
