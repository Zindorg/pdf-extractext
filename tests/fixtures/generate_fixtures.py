#!/usr/bin/env python3
"""Script to generate PDF test fixtures.

Run this script to regenerate test fixtures:
    uv run python tests/fixtures/generate_fixtures.py
"""

import io
import os
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent


def generate_valid_pdf():
    """Generate a valid PDF with text content."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 700, "Hello World")
    c.drawString(100, 680, "This is a test PDF with text content")
    c.drawString(100, 660, "PDF extractext test document")
    c.save()

    buffer.seek(0)
    content = buffer.getvalue()

    filepath = get_fixtures_dir() / "valid.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated valid.pdf ({len(content)} bytes)")


def generate_multipage_pdf():
    """Generate a PDF with 5 pages, each with different text."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for page_num in range(1, 6):
        c.drawString(100, 700, f"Page {page_num}")
        c.drawString(100, 680, f"This is content for page {page_num}")
        c.drawString(100, 660, f"Unique identifier: PAGE_{page_num}_CONTENT")
        if page_num < 5:
            c.showPage()

    c.save()
    buffer.seek(0)
    content = buffer.getvalue()

    filepath = get_fixtures_dir() / "multipage.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated multipage.pdf ({len(content)} bytes, 5 pages)")


def generate_corrupted_pdf():
    """Generate a PDF with invalid header."""
    content = b"%PDF-0.0\ninvalid data here\x00\x01\x02\x03"

    filepath = get_fixtures_dir() / "corrupted.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated corrupted.pdf ({len(content)} bytes)")


def generate_zero_bytes_pdf():
    """Generate a truly empty file (0 bytes)."""
    filepath = get_fixtures_dir() / "zero_bytes.pdf"
    with open(filepath, "wb") as f:
        pass  # Create empty file

    print(f"Generated zero_bytes.pdf (0 bytes)")


def generate_large_pdf():
    """Generate a PDF larger than 10MB (~11MB) using binary padding."""
    from pathlib import Path

    # Read base valid.pdf content
    valid_pdf_path = get_fixtures_dir() / "valid.pdf"
    if not valid_pdf_path.exists():
        # Generate valid.pdf first if it doesn't exist
        generate_valid_pdf()

    with open(valid_pdf_path, "rb") as f:
        base_content = f.read()

    # Calculate padding needed to reach ~11MB
    target_size = 11 * 1024 * 1024  # 11MB
    padding_needed = target_size - len(base_content)

    # Create a minimal PDF structure with a large stream object
    stream_content = b"X" * padding_needed

    pdf_content = (
        b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """
        + str(len(stream_content)).encode()
        + b""" 
>>
stream
"""
        + stream_content
        + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
"""
        + str(206 + len(stream_content) + 50).encode()
        + b"""
%%EOF"""
    )

    filepath = get_fixtures_dir() / "large.pdf"
    with open(filepath, "wb") as f:
        f.write(pdf_content)

    print(f"Generated large.pdf ({len(pdf_content):,} bytes, ~11 MB)")


def generate_unicode_pdf():
    """Generate a PDF with unicode content."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Register a font that supports unicode
    try:
        # Try to use DejaVu Sans if available
        c.setFont("Helvetica", 12)
    except:
        pass

    # Basic ASCII with accents
    c.drawString(100, 700, "Hola Mundo con tildes: á é í ó ú")
    c.drawString(100, 680, "Letra enie: cancion, monotonia")
    c.drawString(100, 660, "Mayusculas: ÁÉÍÓÚ Ñ")
    c.drawString(100, 640, "Palabras: otorrinolaringologo, año, paraiso")

    # Try to add emoji (may not render in all PDF viewers)
    try:
        c.drawString(100, 620, "Emoji test: test")
    except:
        c.drawString(100, 620, "Emoji test: [skipped]")

    c.save()
    buffer.seek(0)
    content = buffer.getvalue()

    filepath = get_fixtures_dir() / "unicode.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated unicode.pdf ({len(content)} bytes)")


def generate_image_only_pdf():
    """Generate a PDF with only an image, no extractable text."""
    from reportlab.lib.utils import ImageReader
    import io as bio

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Create a simple colored rectangle as image
    # Since we don't have an external image, create a simple one in memory
    from PIL import Image

    img = Image.new('RGB', (200, 100), color='red')
    img_buffer = bio.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    img_reader = ImageReader(img_buffer)
    c.drawImage(img_reader, 100, 600, width=200, height=100)

    c.save()
    buffer.seek(0)
    content = buffer.getvalue()

    filepath = get_fixtures_dir() / "image_only.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated image_only.pdf ({len(content)} bytes)")


def generate_empty_pdf():
    """Generate an empty PDF (valid PDF with 0 pages)."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    content = buffer.getvalue()

    filepath = get_fixtures_dir() / "empty.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Generated empty.pdf ({len(content)} bytes, 0 pages)")


def main():
    """Generate all test fixtures."""
    fixtures_dir = get_fixtures_dir()

    # Ensure fixtures directory exists
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    print("Generating PDF test fixtures...")
    print("-" * 50)

    generate_valid_pdf()
    generate_multipage_pdf()
    generate_corrupted_pdf()
    generate_zero_bytes_pdf()
    generate_large_pdf()
    generate_unicode_pdf()
    generate_image_only_pdf()
    generate_empty_pdf()

    print("-" * 50)
    print("All fixtures generated successfully!")

    # List generated files
    print("\nGenerated files:")
    for f in sorted(fixtures_dir.glob("*.pdf")):
        size = f.stat().st_size
        print(f"  {f.name}: {size:,} bytes")


if __name__ == "__main__":
    main()
