import pypdf
import io
import requests
import os
import shutil
from dotenv import load_dotenv

load_dotenv()
folder = os.getenv('PDF_FOLDER')

def remove_pdf(pdf: str) -> str:
    if pdf.lower() == "all":
        shutil.rmtree(folder)
        os.makedirs(folder)
    else:
        safe_filename = os.path.basename(pdf)
        file_path = os.path.join(folder, safe_filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
    return "succesfully removed the pdf(s)"

if __name__ == "__main__":
    print("placeholder")