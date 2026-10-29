"""Best-effort text extraction. OCR dependencies remain optional for local demos."""
from pathlib import Path


def extract_text(data: bytes, filename: str) -> str | None:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return data.decode("utf-8", errors="replace")[:100_000]
    if suffix == ".pdf":
        try:
            import fitz  # PyMuPDF, intentionally optional
            pdf = fitz.open(stream=data, filetype="pdf")
            return "\n".join(page.get_text() for page in pdf)[:100_000] or None
        except ImportError:
            return None
    return None
