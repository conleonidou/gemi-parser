import pandas as pd

def prepare_line_items_table(line_items):
    """Create a DataFrame for line items"""
    return pd.DataFrame([
        {
            'Description': item.description,
            'Quantity': item.quantity,
            'Unit': item.unit or '',
            'Unit Price': f"${item.unit_price:.2f}",
            'Total Amount': f"${item.amount:.2f}"
        } for item in line_items
    ])

def prepare_vat_table(vat_items):
    """Create a DataFrame for VAT details"""
    return pd.DataFrame([
        {
            'Amount': f"${vat.amount:.2f}",
            'Tax Rate': f"{vat.tax_rate or 0}%",
            'Tax Amount': f"${vat.tax_amount or 0:.2f}",
            'Total Amount': f"${vat.total_amount:.2f}"
        } for vat in vat_items
    ])