# =========================================================
# CHECKLIST PLATEAU ICU V2 — CONNECTÉ FLOW + PHARMACO
# =========================================================

from pharmaco import detect_drug, get_drug


def checklist_v2(flow_result: dict, text: str):
    t = text.lower()

    resp = flow_result["scores"]["resp"]
    hemo = flow_result["scores"]["hemo"]
    infect = flow_result["scores"]["infect"]
    neuro = flow_result["scores"]["neuro"]

    checklist = []

    # =====================================================
    # BASE PLATEAU (TOUS CAS)
    # =====================================================
    base = [
        "☐ Scope monitorage continu",
        "☐ Voies veineuses périphériques x2",
        "☐ Oxygène disponible",
        "☐ Aspiration fonctionnelle",
        "☐ Chariot d'urgence prêt"
    ]

    checklist.append(("🧰 BASE", base))

    # =====================================================
    # RESPIRATOIRE
    # =====================================================
    if resp >= 2:
        resp_block = [
            "☐ Pré-oxygénation",
            "☐ Masque haute concentration / VNI prêt",
            "☐ Intubation matériel complet",
            "☐ Capnographie fonctionnelle"
        ]
        checklist.append(("🫁 RESPIRATOIRE", resp_block))

    # =====================================================
    # HÉMODYNAMIQUE
    # =====================================================
    if hemo >= 2:
        drug = detect_drug(text)
        drug_data = get_drug(drug) if drug else None

        hemo_block = [
            "☐ TA invasive si disponible",
            "☐ Remplissage cristalloïdes prêt",
            "☐ Noradrénaline préparée en seringue",
        ]

        if drug_data:
            hemo_block.append(f"☐ Perfusion active : {drug}")

        checklist.append(("🫀 HÉMODYNAMIQUE", hemo_block))

    # =====================================================
    # INFECTIEUX
    # =====================================================
    if infect >= 2:
        infect_block = [
            "☐ Hémocultures si possible",
            "☐ ATB probabiliste préparé",
            "☐ Contrôle source infectieuse",
            "☐ Lactates contrôlés"
        ]
        checklist.append(("🦠 INFECTIEUX", infect_block))

    # =====================================================
    # NEUROLOGIQUE
    # =====================================================
    if neuro >= 2:
        neuro_block = [
            "☐ GCS évalué",
            "☐ Protection des voies aériennes",
            "☐ Sédation disponible",
            "☐ Surveillance pupilles"
        ]
        checklist.append(("🧠 NEUROLOGIQUE", neuro_block))

    # =====================================================
    # OUTPUT FORMATÉ
    # =====================================================
    return checklist
