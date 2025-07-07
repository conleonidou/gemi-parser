import tempfile
import os
from google import genai
import streamlit as st
from pydantic import BaseModel
from src.models.invoice import Invoice
from dotenv import load_dotenv
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
