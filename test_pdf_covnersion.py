from PIL import Image
import fitz  # PyMuPDF
import os

def convert_image_to_pdf(image_path, output_pdf_path="converted_invoice.pdf"):
    """Convert an image to a valid PDF and save it to disk"""
    image = Image.open(image_path).convert("RGB")
    image.save(output_pdf_path, "PDF")
    print(f"PDF successfully saved to: {output_pdf_path}")
    return output_pdf_path

def test_pdf_validity(pdf_path):
    """Open the PDF using PyMuPDF to verify it's valid"""
    try:
        doc = fitz.open(pdf_path)
        print(f"PDF opened successfully. Number of pages: {len(doc)}")
        doc.close()
    except Exception as e:
        print(f"Failed to open PDF: {e}")

if __name__ == "__main__":
    # Replace with your image path
    image_path = "Media.jpg"  # or .png

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
    else:
        output_pdf_path = "converted_invoice.pdf"
        pdf_path = convert_image_to_pdf(image_path, output_pdf_path)
        test_pdf_validity(pdf_path)