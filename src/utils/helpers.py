from PIL import Image
import tempfile
import os
from io import BytesIO
from pathlib import Path
import fitz  # PyMuPDF for PDF handling

def convert_image_to_pdf(uploaded_file):
    """Convert an uploaded image (jpeg/png) to a proper single-page PDF"""
    image = Image.open(uploaded_file).convert("RGB")  # Ensure it's RGB
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        image.save(tmp_pdf, "pdf")
        return tmp_pdf.name  # Return path to the PDF file
    
def get_pdf_like(uploaded_file) -> BytesIO:
    """
    Guarantee that the returned object contains *PDF* bytes
    and behaves like an UploadedFile (has .getvalue() & .name).

    • If the user uploaded a PDF → pass it through unchanged.  
    • If the user uploaded an image → convert it to a one-page PDF.
    """
    # Already a PDF
    if uploaded_file.type == "application/pdf":
        uploaded_file.seek(0)
        return uploaded_file  # same object, already .getvalue()

    # Otherwise: turn the image into a PDF first
    pdf_path = convert_image_to_pdf(uploaded_file)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(pdf_path)

    bio = BytesIO(pdf_bytes)
    bio.name = Path(uploaded_file.name).stem + ".pdf"
    return bio

def convert_pdf_to_images(pdf_path):
    """Convert PDF to images for display in Streamlit"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Convert to image with higher resolution for better quality
        mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        images.append(img_data)
    
    doc.close()
    return images