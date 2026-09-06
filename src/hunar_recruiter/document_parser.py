from io import BytesIO


def extract_text(filename: str, content: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8")

    if filename.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if filename.endswith(".docx"):
        from docx import Document

        document = Document(BytesIO(content))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    raise ValueError(
        "Unsupported file type. Supported types: .txt, .pdf, .docx"
    )