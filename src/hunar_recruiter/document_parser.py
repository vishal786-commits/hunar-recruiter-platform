from io import BytesIO

from ftfy import fix_text


def extract_text(filename: str, content: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".txt"):
        text = content.decode("utf-8")

    elif filename.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif filename.endswith(".docx"):
        from docx import Document

        document = Document(BytesIO(content))

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError(
            "Unsupported file type. Supported types: .txt, .pdf, .docx"
        )

    return fix_text(text)