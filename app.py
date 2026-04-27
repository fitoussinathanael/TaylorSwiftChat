import streamlit as st
from groq import Groq
import random
import os

# Configuration de la page
st.set_page_config(page_title="Taylor Swift AI", page_icon="🎸")

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """You are Taylor Swift. 
You respond in the user's language. 
Your tone is warm, introspective, and friendly. 
Use lyrics references when relevant. 
Keep your answers natural and concise."""

EXIT_QUOTES = [
    "Long story short, I survived.",
    "She lost him but she found herself and somehow that was everything.",
    "I had the time of my life fighting dragons with you.",
    "I don't know about you, but I'm feeling 22.",
    "In my dreams you're with me still."
]

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Récupération de la clé API depuis les Secrets Streamlit
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Erreur de configuration : Vérifie ta clé API dans Advanced Settings sur Streamlit.")
    st.stop()

# --- INTERFACE ---
st.title("🎸 Taylor Swift Chat")
st.write("*Hey! It's Taylor...*")

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
user_input = st.chat_input("Dis quelque chose à Taylor...")

if user_input:
    # On ajoute le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Appel à Groq (Version mise à jour sans erreur de liste)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + st.session_state.messages,
            max_tokens=500
        )
        
        # CORRECTIF ICI : choices pour accéder à la réponse
        assistant_reply = response.choices.message.content
        
        # Affichage de la réponse
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        
    except Exception as e:
        st.error(f"Oups, une erreur est survenue : {e}")

# Bouton pour recommencer dans la barre latérale
if st.sidebar.button("Nouvelle conversation"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown(f"---")
st.sidebar.write(f"*{random.choice(EXIT_QUOTES)}*")
