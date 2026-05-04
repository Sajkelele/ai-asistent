import os
from pypdf import PdfReader

def load_documents():
    texts = []

    folder = os.path.join(os.getcwd(), "Dany", "documents")

    print("📂 hledám:", folder)

    if not os.path.exists(folder):
        print("❌ složka nenalezena")
        return texts

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if file.endswith(".pdf"):
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            texts.append(text)

    return texts