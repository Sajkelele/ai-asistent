import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store

# 🔥 select s "Specifické"
def select_with_custom(label, options):
    choice = st.selectbox(label, options + ["Specifické"])
    if choice == "Specifické":
        return st.text_input(f"{label} - upřesnění")
    return choice

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
@st.cache_resource
def get_vectorstore():
    return create_vector_store()

vectorstore = get_vectorstore()

st.title("AI Generátor technické zprávy")

# 🔥 STEP STATE
if "step" not in st.session_state:
    st.session_state.step = 1

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1


# 🔹 STEP 1
if st.session_state.step == 1:
    st.header("1️⃣ Identita a pozemek")

    lokalita = st.text_input("Lokalita")

    typ_uzemi = select_with_custom(
        "Typ území",
        ["v zastavěné části", "v nezastavěné části", "v chatové oblasti"]
    )

    if st.button("Další"):
        st.session_state.lokalita = lokalita
        st.session_state.typ_uzemi = typ_uzemi
        next_step()


# 🔹 STEP 2
elif st.session_state.step == 2:
    st.header("2️⃣ Stavba")

    pocet_bytu = select_with_custom("Počet bytů", ["1", "2", "3"])
    pocet_np = select_with_custom("Počet NP", ["1", "2", "3"])
    podkrovi = st.radio("Podkroví", ["ano", "ne"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Zpět"):
            prev_step()

    with col2:
        if st.button("Další"):
            st.session_state.pocet_bytu = pocet_bytu
            st.session_state.pocet_np = pocet_np
            st.session_state.podkrovi = podkrovi
            next_step()


# 🔹 STEP 3
elif st.session_state.step == 3:
    st.header("3️⃣ Technické řešení")

    strecha = select_with_custom(
        "Typ střechy",
        ["šikmá", "plochá", "pultová", "kombinovaná"]
    )

    vytapeni = select_with_custom(
        "Vytápění",
        ["tepelné čerpadlo vzduch-voda", "plyn", "elektřina", "biomasa"]
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Zpět"):
            prev_step()

    with col2:
        if st.button("Další"):
            st.session_state.strecha = strecha
            st.session_state.vytapeni = vytapeni
            next_step()


# 🔹 STEP 4
elif st.session_state.step == 4:
    st.header("4️⃣ Generování zprávy")

if st.button("Vygenerovat zprávu"):

    data = {
        "lokalita": st.session_state.lokalita,
        "typ_uzemi": st.session_state.typ_uzemi,
        "pocet_bytu": st.session_state.pocet_bytu,
        "pocet_np": st.session_state.pocet_np,
        "podkrovi": st.session_state.podkrovi,
        "strecha": st.session_state.strecha,
        "vytapeni": st.session_state.vytapeni
    }

    docs = vectorstore.similarity_search("technická zpráva", k=3)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
Použij tyto dokumenty jako vzor:
{context}

Vytvoř kompletní technickou zprávu.

Použij tyto údaje:
{data}

❗ NEPOUŽÍVEJ placeholdery.
❗ Piš jako zkušený projektant.
"""

    # 🔥 TADY JE SPINNER
    with st.spinner("Generuji zprávu..."):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

    st.subheader("Výstup")
    st.write(response.choices[0].message.content)

    if st.button("Zpět"):
        prev_step()
