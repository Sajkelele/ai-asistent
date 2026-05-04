import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store
def select_with_custom(label, options):
    choice = st.selectbox(label, options + ["Specifické"], key=label)
    if choice == "Specifické":
        return st.text_input(f"{label} - upřesnění", key=label+"_custom")
    return choice
form_fields = [
    ("Lokalita", "text", None),
    ("Typ území", "select", ["v zastavěné části", "v nezastavěné části", "chatová oblast"]),
    ("Počet bytů", "select", ["1", "2", "3"]),
    ("Počet NP", "select", ["1", "2", "3"]),
    ("Podkroví", "radio", ["ano", "ne"]),
    ("Podsklepení", "radio", ["ano", "ne"]),
    ("Půdorys", "select", ["obdélník", "čtverec", "L tvar"]),
    ("Konstrukce", "select", ["zděná", "dřevostavba", "kombinovaná"]),
    ("Typ střechy", "select", ["šikmá", "plochá", "pultová", "kombinovaná"]),
    ("Vytápění", "select", ["tepelné čerpadlo", "plyn", "elektřina", "biomasa"]),
    ("Voda", "select", ["vodovod", "studna"]),
    ("Kanalizace", "select", ["kanalizace", "ČOV", "septik"]),
    ("Elektřina", "select", ["ano", "ne"]),
    ("Plyn", "select", ["ano", "ne"])
]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_resource
def get_vectorstore():
    return create_vector_store()

vectorstore = get_vectorstore()

st.title("AI Asistent projektanta")

data = {}

with st.sidebar:
    st.header("Parametry projektu")

    for label, field_type, options in form_fields:
        if field_type == "text":
            value = st.text_input(label, key=label)

        elif field_type == "select":
            value = select_with_custom(label, options)

        elif field_type == "radio":
            value = st.radio(label, options, key=label)

        data[label] = value
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
Použij tyto dokumenty jako vzor:
{context}

Parametry projektu:
""" + "\n".join([f"- {k}: {v}" for k, v in data.items()]) + """

---

Vytvoř profesionální technickou zprávu.

❗ POVINNĚ:
1. Použij strukturu a nadpisy z dodaných dokumentů (např.:
   - Celkový popis území stavby
   - Urbanistické a architektonické řešení
   - Stavebně technické řešení
   - atd.)

2. Zachovej formát jako ve skutečné projektové dokumentaci

3. Pokud některé údaje chybí:
   👉 napiš otázky NA KONCI dokumentu:
   "Doplňující otázky pro projektanta:"

4. NEPOUŽÍVEJ:
   - [doplnit]
   - [uveďte]

5. Piš jako zkušený autorizovaný projektant

---

Výstup:
- kompletní dokument
- + seznam otázek na konci
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
