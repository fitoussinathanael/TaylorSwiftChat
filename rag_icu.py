from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# -----------------------------
# MODELE NLP (gratuit, léger)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# BASE ICU (version test)
# 👉 tu pourras remplacer par HUG plus tard
# -----------------------------
documents = [
    "Midazolam compatible avec fentanyl en Y-site selon données ICU.",
    "Midazolam incompatible avec solutions alcalines.",
    "Noradrenaline nécessite une ligne dédiée en réanimation.",
    "Amiodarone compatibilité variable selon concentration et solvant.",
    "Ceftriaxone incompatible avec calcium en perfusion IV.",
    "Propofol nécessite une perfusion dédiée en seringue électrique.",
    "Insuline IV nécessite contrôle glycémique strict et ligne dédiée.",
    "Vasopresseurs doivent être administrés sur voie centrale si possible.",
    "Potassium chlorure jamais en bolus IV direct."
]

# -----------------------------
# EMBEDDINGS (vectorisation)
# -----------------------------
embeddings = model.encode(documents)

index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings))

# -----------------------------
# FONCTION DE RECHERCHE ICU
# -----------------------------
def search_icu(query, k=3):
    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k)

    results = []
    for i in indices[0]:
        results.append(documents[i])

    return results
