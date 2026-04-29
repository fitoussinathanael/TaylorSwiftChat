# =========================================================
# PERFUSION ENGINE ICU — VERSION PRO STABLE
# =========================================================

import re
from pharmaco_core import find_drug, is_perfusible, fallback_message


# =========================================================
# DETECTION INPUT (robuste terrain)
# =========================================================

def detect_input(text):
    t = text.lower()

    drug_name, drug_data = find_drug(t)

    # poids robuste : accepte "70", "70kg", "70 k"
    weight = None
    w = re.findall(r'(\d{2,3})', t)
    if w:
        try:
            weight = int(w[0])
        except:
            weight = None

    return drug_name, drug_data, weight


# =========================================================
# CALCUL PERFUSION
# =========================================================

def calc_perfusion(dose, weight, conc, unit):

    try:
        if unit == "µg/kg/min":
            return round(((dose * weight * 60) / (conc * 1000)) * 2) / 2

        if unit == "mg/kg/h":
            return round(((dose * weight) / conc) * 2) / 2

        if unit == "µg/kg/h":
            return round(((dose * weight) / conc) * 2) / 2

        return None

    except:
        return None


# =========================================================
# ARRONDI TERRAIN IDE
# =========================================================

def round_ide(value):
    """
    Arrondi pratique IDE (multiple simple)
    """
    if value is None:
        return None
    return round(value)


def multiply_12(value):
    """
    Conversion seringue électrique (12h)
    """
    if value is None:
        return None
    return round(value * 12, 1)


# =========================================================
# GENERATE TABLE
# =========================================================

def build_perfusion_output(drug_name, drug_data, weight):

    # -------------------------
    # Cas non trouvé
    # -------------------------
    if not drug_name:
        return fallback_message("inconnu")

    # -------------------------
    # Cas non perfusable
    # -------------------------
    if not is_perfusible(drug_data):
        return f"""
💊 {drug_name.upper()}

Classe : {drug_data.get("classe","-")}

📌 POSOLOGIE :
{drug_data.get("dose_standard","Non précisée")}

⚠️ Médicament non perfusable en continu
"""

    # -------------------------
    # Cas perfusion
    # -------------------------
    unit = drug_data["unit"]
    conc = drug_data["conc_default"]
    steps = drug_data["steps"]

    out = f"\n💉 {drug_name.upper()} — {weight} kg\n\n"
    out += "DOSE | IDEAL | RÉEL | ×12\n"
    out += "-----------------------------\n"

    for dose in steps:

        real = calc_perfusion(dose, weight, conc, unit)
        ideal = round_ide(real)
        x12 = multiply_12(real)

        out += f"{dose} | {ideal} | {real} | {x12}\n"

    return out


# =========================================================
# MAIN ENTRY
# =========================================================

def perfusion_response(text):

    drug_name, drug_data, weight = detect_input(text)

    if not weight:
        return "💉 Données manquantes (ex: noradrenaline 70 kg)"

    return build_perfusion_output(drug_name, drug_data, weight)
