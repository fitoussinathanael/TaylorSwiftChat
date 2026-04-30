# =========================================================
# PERFUSION ICU V2 — CALCUL RÉA PROPRE
# =========================================================

from pharmaco import get_drug

# =========================================================
# CALCUL STANDARD
# =========================================================
def calc_ml_h(dose, weight, conc, unit):
    """
    dose : µg/kg/min ou mg/kg/h
    conc : mg/mL ou équivalent
    """

    if unit == "µg/kg/min":
        return round(((dose * weight * 60) / (conc * 1000)), 2)

    elif unit == "mg/kg/h":
        return round((dose * weight) / conc, 2)

    else:
        return None


# =========================================================
# MÉTHODE IDE ×12
# =========================================================
def calc_x12(value):
    return round(value * 12, 1)


# =========================================================
# GÉNÉRATION TABLEAU PERFUSION
# =========================================================
def build_perfusion_table(drug_name, weight):

    drug = get_drug(drug_name)
    if not drug:
        return None

    table = []

    for dose in drug["dose"]:

        ideal = calc_ml_h(dose, weight, drug["conc"], drug["unit"])
        real = calc_x12(ideal)

        # statut sécurité
        if dose >= drug["max"] * 0.8:
            status = "🔴 LIMITE"
        elif dose >= drug["dose"][-1]:
            status = "🟠 HAUT"
        else:
            status = "🟢 OK"

        table.append({
            "dose": dose,
            "ideal": ideal,
            "real": real,
            "status": status
        })

    return table


# =========================================================
# AFFICHAGE STREAMLIT
# =========================================================
def display_perfusion(st, drug_name, weight):

    drug = get_drug(drug_name)

    if not drug:
        st.error("❌ Médicament non trouvé")
        return

    st.subheader(f"💉 PERFUSION ICU — {drug_name.upper()}")

    st.markdown(f"""
📖 {drug['classe']}  
🎯 {drug['cible']}  
⚖️ Poids : {weight} kg  
""")

    table = build_perfusion_table(drug_name, weight)

    st.markdown("### 📊 Tableau perfusion")

    cols = st.columns(4)
    cols[0].markdown("**Dose**")
    cols[1].markdown("**mL/h (idéal)**")
    cols[2].markdown("**mL/h (×12)**")
    cols[3].markdown("**Statut**")

    for row in table:
        c1, c2, c3, c4 = st.columns(4)

        c1.write(row["dose"])
        c2.write(row["ideal"])
        c3.write(row["real"])
        c4.write(row["status"])

        if row["status"] == "🔴 LIMITE":
            st.error("🚨 Dose élevée — surveillance rapprochée")
        elif row["status"] == "🟠 HAUT":
            st.warning("⚠️ Dose haute")

    st.info("Titration progressive recommandée — monitorage continu")
