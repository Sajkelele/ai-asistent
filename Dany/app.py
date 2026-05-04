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
Použij následující technické zprávy jako vzor:
{context}

Parametry projektu:
{params_text}

---

Úkol:
Jsi zkušený autorizovaný projektant.

Na základě dodaných podkladů vytvoř profesionální technickou zprávu.

---

POVINNÁ STRUKTURA:
Použij reálné nadpisy jako v projektové dokumentaci, například:

1. Celkový popis území stavby  
2. Urbanistické a architektonické řešení  
3. Stavebně technické řešení  
4. Dopravní řešení  
5. Technická infrastruktura  
6. Vliv stavby na okolí  
7. Organizace výstavby  

---

PRAVIDLA:
- Piš souvislý odborný text (ne body)
- NEPOUŽÍVEJ placeholdery typu [doplnit], [xxx]
- Pokud údaj chybí → odhadni realisticky podle kontextu
- Pokud nelze odhadnout → nech místo prázdné, ale nepiš závorky

---

DOPLŇUJÍCÍ OTÁZKY:
Na konec dokumentu přidej sekci:

"Doplňující otázky pro projektanta:"

a napiš konkrétní otázky na chybějící údaje (např. rozměry, materiály, napojení atd.)

---

ROZHODOVÁNÍ:
- Pokud uživatel chce dokument → vytvoř celý dokument
- Pokud se jen ptá → odpověz normálně

---

VÝSTUP:
- kompletní technická zpráva
- + otázky na konci
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
