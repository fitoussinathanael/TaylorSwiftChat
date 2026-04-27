import streamlit as st
from groq import Groq
import random

# 1. Configuration de la page
st.set_page_config(page_title="Taylor Swift AI", page_icon="🎸")

# 2. Initialisation de Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Clé API manquante dans les Secrets Streamlit.")
    st.stop()

# 3. Personnalité de Taylor
SYSTEM_PROMPT = "You are Taylor Swift. Respond in the user's language. Be warm and use lyric references."

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Interface
st.title("🎸 Taylor Swift Chat")
st.write("*Hey! It's Taylor...*")

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Logique du Chat
user_input = st.chat_input("Dis quelque chose à Taylor...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        )

        assistant_reply = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        st.error(f"Erreur : {e}")

# 6. Barre latérale
if st.sidebar.button("Nouvelle conversation"):
    st.session_state.messages = []
    st.rerun()
