import streamlit as st
from groq import Groq

st.title("Hospital Engine - DEBUG API")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    st.success("Groq connecté OK")
except Exception as e:
    st.error(f"Erreur API : {e}")
    st.stop()

user_input = st.text_input("Test input")

if user_input:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )

    st.write(response.choices[0].message.content)
