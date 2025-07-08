import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF for PDF to image conversion
from src.services.invoice_processor import process_invoice, extract_doc_layout, draw_bounding_boxes
from src.utils.data_preparation import prepare_line_items_table, prepare_vat_table
from streamlit_pdf_viewer import pdf_viewer

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

# Configure page
st.set_page_config(page_title="Invoice Intelligence", layout="wide")
st.title("Invoice Intelligent OCR")

# Initialize session state
if 'invoice_data' not in st.session_state:
    st.session_state.invoice_data = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Sidebar for file upload and PDF preview
with st.sidebar:    
    # File uploader in sidebar
    uploaded_file = st.file_uploader("Upload an invoice (pdf)", type=['pdf'])
    # PDF Preview 
    if uploaded_file is not None:
        st.subheader("PDF Preview")
        # Using native document display
        with st.expander("View PDF", expanded=True):
            binary_data = uploaded_file.getvalue()
            pdf_viewer(input=binary_data,
                        width=700)

# Check if a new file is uploaded
if uploaded_file is not None:
    # Only process if the uploaded file is different from the previously processed file
    if uploaded_file != st.session_state.uploaded_file:
        st.session_state.invoice_data = process_invoice(uploaded_file)
        st.session_state.uploaded_file = uploaded_file

# Render invoice details if data exists
if st.session_state.invoice_data is not None:
    invoice_data = st.session_state.invoice_data
    
    # Invoice Details
    st.subheader("Parsed Invoice Details")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        st.write(f"**Invoice ID:** {invoice_data.invoice_id}")
        st.write(f"**Date:** {invoice_data.invoice_date}")
        st.write(f"**Payment Terms:** {invoice_data.payment_terms}")
    
    with col2:
        st.subheader("Supplier Information")
        st.write(f"**Name:** {invoice_data.supplier.name}")
        if invoice_data.supplier.email:
            st.write(f"**Email:** {invoice_data.supplier.email}")
        if invoice_data.supplier.phone:
            st.write(f"**Phone:** {invoice_data.supplier.phone}")
    
    # Line Items Table
    st.subheader("Line Items")
    line_items_df = prepare_line_items_table(invoice_data.line_items)
    st.dataframe(line_items_df, use_container_width=True)
    
    # VAT Details Table
    st.subheader("VAT Details")
    vat_df = prepare_vat_table(invoice_data.vat)
    st.dataframe(vat_df, use_container_width=True)

    # Extracted fields with bounding boxes
    st.subheader("Extracted fields")
    try:
        with st.spinner("Processing field detection..."):
            # Reset file pointer
            uploaded_file.seek(0)
            layout = extract_doc_layout(uploaded_file.getvalue(), invoice_data)
            
            # Reset file pointer again
            uploaded_file.seek(0)
            output_pdf_path = draw_bounding_boxes(uploaded_file, layout)
        
        # Display PDF with bounding boxes
        with st.expander("PDF with Detected Fields", expanded=True):
            try:
                # Convert PDF to images for display
                images = convert_pdf_to_images(output_pdf_path)
                
                # Display images
                for i, img_data in enumerate(images):
                    st.image(img_data, caption=f"Page {i+1} - Fields highlighted in red", use_container_width=True)
                
                # Provide download button for the processed PDF
                with open(output_pdf_path, "rb") as file:
                    pdf_data = file.read()
                
                st.download_button(
                    label="Download PDF with Bounding Boxes",
                    data=pdf_data,
                    file_name=f"processed_{uploaded_file.name}",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error displaying PDF with bounding boxes: {str(e)}")
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(output_pdf_path)
                except:
                    pass  # File might already be deleted
    
    except Exception as e:
        st.error(f"Error processing field detection: {str(e)}")

    # Add download button for JSON
    st.download_button(
        label="Download Complete JSON",
        data=invoice_data.model_dump_json(indent=2),
        file_name="invoice_data.json",
        mime="application/json"
    )