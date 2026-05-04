from openai import OpenAI
from vector_store import create_vector_store

client = OpenAI()

# vytvoření databáze dokumentů
vectorstore = create_vector_store()

# 👉 TADY JE TVŮJ "FORMULÁŘ" (zatím napevno)
data = {
    "lokalita": "obec Lukov",
    "typ_uzemi": "v zastavěné části",
    "pocet_bytu": "1",
    "pocet_osob": "4",
    "pudorys": "obdélník",
    "pocet_np": "2",
    "podkrovi": "ano",
    "podsklepeni": "částečně",
    "konstrukce": "zděný objekt",
    "strecha": "šikmá",
    "vytapeni": "tepelné čerpadlo vzduch-voda",
    "elektrina": "přípojka z distribuční sítě",
    "plyn": "není napojen"
}

while True:
    query = input("\nZadej typ dokumentu (např. technická zpráva): ")

    docs = vectorstore.similarity_search(query, k=3)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
Použij tyto dokumenty jako vzor:
{context}

Vytvoř kompletní technickou zprávu.

Použij tyto údaje:
- Lokalita: {data['lokalita']}
- Typ území: {data['typ_uzemi']}
- Počet bytových jednotek: {data['pocet_bytu']}
- Počet osob: {data['pocet_osob']}
- Půdorys: {data['pudorys']}
- Počet NP: {data['pocet_np']}
- Podkroví: {data['podkrovi']}
- Podsklepení: {data['podsklepeni']}
- Konstrukční systém: {data['konstrukce']}
- Typ střechy: {data['strecha']}
- Vytápění: {data['vytapeni']}
- Elektrická energie: {data['elektrina']}
- Plyn: {data['plyn']}

❗ NEPOUŽÍVEJ placeholdery.
❗ Piš jako zkušený projektant.
❗ Doplň realistické hodnoty, pokud něco chybí.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n--- VÝSTUP ---\n")
    print(response.choices[0].message.content)