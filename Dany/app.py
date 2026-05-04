import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store

# 🔥 select s "Specifické"
def select_with_custom(label, options):
    choice = st.selectbox(label, options + ["Specifické"], key=label)
    if choice == "Specifické":
        return st.text_input(f"{label} - upřesnění", key=label+"_custom")
    return choice

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def get_vectorstore():
    return create_vector_store()

vectorstore = get_vectorstore()

st.title("AI Asistent projektanta")

# 🔹 SIDEBAR = PARAMETRY
with st.sidebar:
    st.header("Parametry projektu")

    data = {}

    data["Lokalita"] = st.text_input("Lokalita")

    data["Typ území"] = select_with_custom(
        "Typ území",
        ["v zastavěné části", "v nezastavěné části", "chatová oblast"]
    )

    data["Počet bytů"] = select_with_custom("Počet bytů", ["1", "2", "3"])
    data["Počet NP"] = select_with_custom("Počet NP", ["1", "2", "3"])
    data["Podkroví"] = st.radio("Podkroví", ["ano", "ne"])

    data["Typ střechy"] = select_with_custom(
        "Typ střechy",
        ["šikmá", "plochá", "pultová", "kombinovaná"]
    )

    data["Vytápění"] = select_with_custom(
        "Vytápění",
        ["tepelné čerpadlo", "plyn", "elektřina", "biomasa"]
    )

# 🔹 CHAT HISTORIE
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 ZOBRAZENÍ CHATHISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 🔹 INPUT
user_input = st.chat_input("Napiš dotaz nebo 'vygeneruj zprávu'...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n\n".join([d.page_content for d in docs])

    params_text = "\n".join([f"- {k}: {v}" for k, v in data.items()])

    prompt = f"""
Použij tyto dokumenty jako vzor:
{context}

Parametry projektu:
{params_text}

---

Uživatel říká:
{user_input}

---

Pokud uživatel chce vytvořit technickou zprávu:
- použij strukturu (např. Celkový popis území stavby, atd.)
- vytvoř kompletní dokument

Pokud chybí údaje:
- zeptej se na ně

Piš jako zkušený projektant.
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
