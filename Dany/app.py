import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = create_vector_store()

st.title("AI Generátor technické zprávy")

# FORMULÁŘ
lokalita = st.text_input("Lokalita")
typ_uzemi = st.selectbox("Typ území", [
    "v zastavěné části",
    "v nezastavěné části",
    "v chatové oblasti"
])

pocet_bytu = st.selectbox("Počet bytů", ["1", "2", "3"])
pocet_np = st.selectbox("Počet NP", ["1", "2", "3"])
podkrovi = st.radio("Podkroví", ["ano", "ne"])
strecha = st.selectbox("Typ střechy", [
    "šikmá",
    "plochá",
    "pultová",
    "kombinovaná"
])

vytapeni = st.selectbox("Vytápění", [
    "tepelné čerpadlo vzduch-voda",
    "plyn",
    "elektřina",
    "biomasa"
])

# TLAČÍTKO
if st.button("Vygenerovat zprávu"):
    data = {
        "lokalita": lokalita,
        "typ_uzemi": typ_uzemi,
        "pocet_bytu": pocet_bytu,
        "pocet_np": pocet_np,
        "podkrovi": podkrovi,
        "strecha": strecha,
        "vytapeni": vytapeni
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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.subheader("Výstup")
    st.write(response.choices[0].message.content)