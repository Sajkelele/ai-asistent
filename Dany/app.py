# 🔥 HLAVNÍ LOGIKA
if user_input:

    # 🔥 jen pokud chce dokument
    wants_doc = any(word in user_input.lower() for word in [
        "zprávu", "zprava", "dokument", "vytvoř", "vygeneruj"
    ])

    if wants_doc:
        errors = []

        if not data.get("Lokalita"):
            errors.append("Vyplň lokalitu")

        if not data.get("Typ území"):
            errors.append("Vyber typ území")

        if not data.get("Počet NP"):
            errors.append("Vyber počet podlaží")

        if errors:
            for e in errors:
                st.error(e)
            st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})

    docs = vectorstore.similarity_search(user_input, k=3)
    context = "\n\n".join([d.page_content for d in docs])

    params_text = "\n".join([f"- {k}: {v}" for k, v in data.items() if v])

    # 🔥 PROMPT MUSÍ BÝT UVNITŘ if user_input
    prompt = f"""
Použij následující technické zprávy jako vzor:
{context}

Parametry projektu:
{params_text}

---

Jsi AI asistent projektanta.

---

PRAVIDLA:

1. Pokud se uživatel jen ptá (např. "ahoj", "co je ČOV", "jak funguje TČ"):
👉 odpověz normálně jako ChatGPT, stručně a přirozeně

2. Pokud uživatel výslovně chce vytvořit technickou zprávu (např.:
"vygeneruj zprávu", "napiš technickou zprávu", "vytvoř dokument"):
👉 vytvoř kompletní technickou zprávu podle vzorů

---

POKUD TVOŘÍŠ TECHNICKOU ZPRÁVU:

- použij strukturu jako:
  Celkový popis území stavby
  Urbanistické řešení
  Stavebně technické řešení
- piš profesionálně jako projektant
- nepoužívej placeholdery
- pokud chybí údaje → napiš otázky na konec

---

ODPOVĚZ PODLE TOHO, CO UŽIVATEL CHCE.
"""

    with st.chat_message("assistant"):
        with st.spinner("Přemýšlím..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content

            st.session_state.last_output = reply
            st.write(reply)

            # 🔥 WORD EXPORT
            doc = Document()
            doc.add_heading("TECHNICKÁ ZPRÁVA", 0)

            for line in reply.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if len(line) < 60:
                    doc.add_heading(line, level=1)
                else:
                    p = doc.add_paragraph(line)
                    p.paragraph_format.space_after = Pt(10)

            filename = "technicka_zprava.docx"
            if data.get("Lokalita"):
                filename = f"zprava_{data['Lokalita']}.docx"

            doc.save(filename)

            with open(filename, "rb") as f:
                st.download_button(
                    "📄 Stáhnout jako Word",
                    f,
                    file_name=filename
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })
