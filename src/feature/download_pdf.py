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

    for pdf in attachments:
        safe_filename = os.path.basename(pdf.filename)
        file_path = os.path.join(folder, safe_filename)

        await pdf.save(file_path)
    return "succesfully downloaded the pdf(s)"

if __name__ == "__main__":
    print("placeholder")