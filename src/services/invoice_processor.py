import fitz
import tempfile
import os
from google import genai
import streamlit as st
from pydantic import BaseModel
from src.models.invoice import Invoice
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

def initialize_gemini_client():
    """Initialize the Gemini API client"""
    try:
        # API_KEY = st.secrets["GOOGLE_API_KEY"]
        API_KEY = os.getenv("GOOGLE_API_KEY")
        if not API_KEY:
            st.error("Please set your GOOGLE_API_KEY in the .env file")
            st.stop()
        
        client = genai.Client(api_key=API_KEY)
        return client, "gemini-2.5-pro"
    except Exception as e:
        st.error(f"Error initializing Gemini client: {str(e)}")
        st.stop()

def extract_structured_data(file_path: str, model: BaseModel):
    """Extract structured data from a PDF file using the Gemini API"""
    client, model_id = initialize_gemini_client()
    
    # Upload the file to the File API
    file = client.files.upload(
        file=file_path, 
        config={'display_name': file_path.split('/')[-1].split('.')[0]}
    )
    
    # Generate a structured response using the Gemini API
    prompt = f"Εξαγάγετε τα δομημένα δεδομένα από το ακόλουθο τιμολόγιο σε μορφή PDF με χειρόγραφο κείμενο στα ελληνικά. Δεν είναι «Ποκουμάδες» αντί για «Λοκουμάδες». Δώσε ιδιαίτερη προσοχή στη γραμματική στα ελληνικά."
    response = client.models.generate_content(
        model=model_id,
        contents=[prompt, file],
        config={
            'response_mime_type': 'application/json',
            'response_schema': model
        }
    )
    
    return response.parsed

def process_invoice(uploaded_file):
    """Process the uploaded invoice PDF"""
    try:
        with st.spinner('Processing invoice...'):
            # Save uploaded file to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract data from PDF
            invoice_data = extract_structured_data(tmp_file_path, Invoice)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return invoice_data
    except Exception as e:
        st.error(f"Error processing the PDF: {str(e)}")
        return None
    
def extract_doc_layout(uploaded_file, invoice_data):
    # This function should implement the logic to draw bounding boxes
    # on the PDF based on the extracted fields.

    fields_to_draw = {
        "invoice_id": invoice_data.invoice_id,
        "invoice_date": invoice_data.invoice_date,
        "payment_terms": invoice_data.payment_terms,
        "supplier.name": invoice_data.supplier.name,
        "supplier.email": invoice_data.supplier.email,
        "supplier.phone": invoice_data.supplier.phone,
        "line_items": invoice_data.line_items,
        "vat": invoice_data.vat
    }

    fields_to_extract = ["VendorName", "InvoiceDate", "InvoiceTotal", "Items"]
    
    di_client = DocumentIntelligenceClient(
        endpoint=os.environ["AZURE_ENDPOINT"], credential=AzureKeyCredential(os.environ["AZURE_API_KEY"])
    )

    poller = di_client.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=uploaded_file,
        pages=1
        # output_content_format=DocumentContentFormat.MARKDOWN,
    )

    # Wait for the result
    res = poller.result()
    data = res.as_dict()['pages'][0]['words']

    layout = {}
    # for i, item in enumerate(data):
    #     if item['content'] in fields_to_draw.values():
    #         list(fields_to_draw.keys())[list(fields_to_draw.values()).index(item['content'])]: item

    # layout = {
    #     list(fields_to_draw.keys())[list(fields_to_draw.values()).index(item['content'])]: item for i, item in enumerate(data) if item['content'] in fields_to_draw.values()
    # }

    for field in fields_to_extract:
        if len(res['documents']) == 0 or field not in res['documents'][0]['fields'] or 'boundingRegions' not in res['documents'][0]['fields'][field]:
            layout[field] = None
            continue
        
        layout[field] = res['documents'][0]['fields'][field]['boundingRegions'][0]['polygon']
    
    return layout

def draw_bounding_boxes(uploaded_file, layout, inches_multiplier = 72):
    """Draw bounding boxes on the PDF based on the extracted layout"""
    # This function implements the logic to draw bounding boxes
    # on the PDF using a library like PyMuPDF or pdfplumber.

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Load the PDF
    doc = fitz.open(tmp_file_path)
    page_width = doc[0].rect.width

    # Draw red rectangles
    for polygon in layout.values():
        if polygon is None:
            continue
        
        ys = polygon[::2]
        ys = [y * inches_multiplier for y in ys]
        xs = polygon[1::2]
        xs = [x * inches_multiplier for x in xs]

        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)

        # Convert normalized coords to absolute PDF coordinates
        y1_abs = page_width - y0
        y0_abs = page_width - y1
                
        page = doc[0]
        rect = fitz.Rect(
            x0=x0, 
            x1=x1, 
            y0=y0_abs, 
            y1=y1_abs # x1
            )
        page.draw_rect(rect, color=(1, 0, 0), width=1.5)  # RGB: Red

    # Save the modified PDF
    doc.save("output_with_boxes.pdf")
    doc.close()
    
    return