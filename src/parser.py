import docx
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from all pages of a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(docx_path: str) -> str:
    """Extracts text from all paragraphs of a .docx file."""
    doc = docx.Document(docx_path)
    full_text = [
        para.text.strip() for para in doc.paragraphs if para.text.strip()
    ]
    return "\n".join(full_text)


def parse_document(file_path: str) -> str:
    """Determines file type and returns raw text content."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        raise ValueError(
            "Unsupported file type. Please supply a .pdf, .docx, or .txt file."
        )