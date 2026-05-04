import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def get_vectorstore():
    return create_vector_store()

vectorstore = get_vectorstore()

st.title("AI Asistent projektanta")

# 🔹 SIDEBAR (tvůj formulář)
with st.sidebar:
    st.header("Parametry projektu")

    lokalita = st.text_input("Lokalita")
    typ_uzemi = st.selectbox("Typ území", ["zastavěné", "nezastavěné"])
    strecha = st.selectbox("Typ střechy", ["šikmá", "plochá"])
    vytapeni = st.selectbox("Vytápění", ["tepelné čerpadlo", "plyn"])

# 🔹 CHAT PAMĚŤ
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 ZOBRAZENÍ CHATHISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 🔹 INPUT
user_input = st.chat_input("Napiš dotaz...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 🔥 CONTEXT
    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
Použij tyto dokumenty:
{context}

Parametry projektu:
- Lokalita: {lokalita}
- Typ území: {typ_uzemi}
- Střecha: {strecha}
- Vytápění: {vytapeni}

Uživatel říká:
{user_input}

Odpověz jako projektant.
"""

    with st.chat_message("assistant"):
        with st.spinner("Přemýšlím..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
