import streamlit as st
from src.services.invoice_processor import process_invoice
from src.utils.data_preparation import prepare_line_items_table, prepare_vat_table
from streamlit_pdf_viewer import pdf_viewer

# Configure page
st.set_page_config(page_title="Flash Invoice Intelligence", layout="wide")
st.title("Gemi-Parser")

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
    st.subheader("Sample Invoice Details")
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
    
    # Add download button for JSON
    st.download_button(
        label="Download Complete JSON",
        data=invoice_data.model_dump_json(indent=2),
        file_name="invoice_data.json",
        mime="application/json"
    )