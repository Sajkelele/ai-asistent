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

    # 🔥 RESET BUTTON
    if st.button("🔄 Resetovat formulář"):
        st.session_state.clear()
        st.rerun()

    data = {}

    # IDENTITA
    data["Druh stavby"] = select_with_custom(
        "Druh stavby",
        ["Rodinný dům", "Rodinný dvojdům", "Řadový dům", "Rekreační objekt"]
    )

    data["Lokalita"] = st.text_input("Lokalita", placeholder="např. Brno")

    # ÚZEMÍ
    data["Typ území"] = st.selectbox(
        "Typ území",
        ["v zastavěné části", "v nezastavěné části", "v chatové oblasti"],
        index=None,
        placeholder="Vyber..."
    )

    data["Napojení na dopravu"] = select_with_custom(
        "Napojení na dopravu",
        ["stávající sjezd", "nový sjezd", "přes jiný pozemek"]
    )

    # HMOTA
    data["Půdorys"] = select_with_custom(
        "Půdorys",
        ["obdélník", "čtverec", "tvar L", "tvar U", "členitý"]
    )

    data["Počet bytů"] = st.selectbox(
        "Počet bytů",
        ["1", "2", "3"],
        index=None,
        placeholder="Vyber..."
    )

    data["Počet NP"] = st.selectbox(
        "Počet NP",
        ["1", "2", "3"],
        index=None,
        placeholder="Vyber..."
    )

    data["Podkroví"] = st.radio(
        "Podkroví",
        ["ano", "ne"],
        index=None
    )

    data["Podsklepení"] = st.radio(
        "Podsklepení",
        ["ne", "ano", "částečně"],
        index=None
    )

    # TERÉN
    data["Terén"] = select_with_custom(
        "Terén na pozemku",
        ["rovina", "mírný sklon", "prudký svah"]
    )

    # GARÁŽ
    data["Garáž"] = select_with_custom(
        "Garáž",
        ["není", "součást domu", "samostatná"]
    )

    # KONSTRUKCE
    data["Konstrukce"] = select_with_custom(
        "Konstrukční systém",
        ["zděný", "dřevostavba", "beton", "ocel"]
    )

    # ENERGIE
    data["Primární vytápění"] = select_with_custom(
        "Primární zdroj vytápění",
        ["TČ vzduch-voda", "TČ země-voda", "plyn", "elektřina", "biomasa"]
    )

    data["Sekundární zdroj"] = select_with_custom(
        "Sekundární zdroj",
        ["krb", "FVE", "není"]
    )

    # SÍTĚ
    data["Voda"] = select_with_custom(
        "Pitná voda",
        ["vodovod", "studna", "není řešeno"]
    )

    data["Kanalizace"] = select_with_custom(
        "Kanalizace",
        ["kanalizace", "ČOV", "jímka"]
    )

    data["Dešťová voda"] = select_with_custom(
        "Dešťová voda",
        ["vsakování", "retenční nádrž", "kanalizace"]
    )

    data["Elektřina"] = select_with_custom(
        "Elektřina",
        ["nová přípojka", "stávající"]
    )

    data["Plyn"] = select_with_custom(
        "Plyn",
        ["ano", "ne"]
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
