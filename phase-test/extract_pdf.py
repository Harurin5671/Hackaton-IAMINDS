from pypdf import PdfReader
import sys

try:
    reader = PdfReader("IA Minds 2026 R.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
