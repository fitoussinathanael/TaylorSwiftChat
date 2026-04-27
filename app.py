import streamlit as st
from groq import Groq
import random
import os

st.set_page_config(page_title="Taylor Swift AI", page_icon="🎸")

SYSTEM_PROMPT = """You are Taylor Swift. Respond in the user's language. Warm, introspective tone. Use lyrics when relevant. Keep it natural."""

EXIT_QUOTES = [
    "Long story short, I survived.",
    "She lost him but she found herself and somehow that was everything.",
    "I had the time of my life fighting dragons with you.",
    "I don't know about you, but I'm feeling 22.",
    "In my dreams you're with me still."
]

if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Erreur : Vérifie ta clé API dans les Secrets.")
    st.stop()

st.title("🎸 Taylor Swift Chat")
st.write("*Hey! It's Taylor...*")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Dis quelque chose à Taylor...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
            max_tokens=500
        )
        assistant_reply = response.choices.message.content
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        st.error(f"Erreur : {e}")

if st.sidebar.button("Nouvelle conversation"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"*{random.choice(EXIT_QUOTES)}*")
