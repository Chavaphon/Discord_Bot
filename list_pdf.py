import os
from dotenv import load_dotenv

load_dotenv()
folder = os.getenv('PDF_FOLDER')

def list_pdf() -> str:
    pdfs = ""

    for pdf in os.listdir(folder):
        file_path = os.path.join(folder, pdf)
        file_size = os.path.getsize(file_path) / 1024
        
        pdfs += f"- {pdf} ({file_size:.1f} KB)\n"
    return pdfs

if __name__ == "__main__":
    pdf = list_pdf()
    print(pdf)