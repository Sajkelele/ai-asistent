import streamlit as st
import os
from openai import OpenAI
from vector_store import create_vector_store

# 🔥 univerzální select s "Specifické"
def select_with_custom(label, options):
    choice = st.selectbox(label, options + ["Specifické"])
    if choice == "Specifické":
        return st.text_input(f"{label} - upřesnění")
    return choice

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = create_vector_store()

st.title("AI Generátor technické zprávy")

# FORMULÁŘ
lokalita = st.text_input("Lokalita")

typ_uzemi = select_with_custom(
    "Typ území",
    ["v zastavěné části", "v nezastavěné části", "v chatové oblasti"]
)

pocet_bytu = select_with_custom(
    "Počet bytů",
    ["1", "2", "3"]
)

pocet_np = select_with_custom(
    "Počet NP",
    ["1", "2", "3"]
)

podkrovi = st.radio("Podkroví", ["ano", "ne"])

strecha = select_with_custom(
    "Typ střechy",
    ["šikmá", "plochá", "pultová", "kombinovaná"]
)

vytapeni = select_with_custom(
    "Vytápění",
    ["tepelné čerpadlo vzduch-voda", "plyn", "elektřina", "biomasa"]
)

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
