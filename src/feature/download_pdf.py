import pypdf
import io
import requests
import os
from dotenv import load_dotenv

load_dotenv()
folder = os.getenv("PDF_FOLDER")

async def download_pdf(attachments: list) -> str:
    if not os.path.exists(folder):
        os.makedirs(folder)

    skipped = []

    for pdf in attachments:
        safe_filename = os.path.basename(pdf.filename)

        if not safe_filename.lower().endswith(".pdf"):
            skipped.append(safe_filename)
            continue

        file_path = os.path.join(folder, safe_filename)

        await pdf.save(file_path)

    if len(skipped) == len(attachments):
        return "no PDF file found, only PDF files can be saved"
    if skipped:
        return f"succesfully downloaded the pdf(s), skipped non-PDF file(s): {', '.join(skipped)}"
    return "succesfully downloaded the pdf(s)"
