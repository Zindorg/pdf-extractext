"""Genera PDFs reales en memoria para los tests (vía reportlab)."""

from io import BytesIO

from reportlab.pdfgen import canvas


def build_pdf(*pages: str) -> bytes:
    """Devuelve un PDF con una página por cada texto recibido.

    Un texto vacío produce una página sin contenido extraíble.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    for text in pages or ("",):
        if text:
            pdf.drawString(72, 720, text)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()
