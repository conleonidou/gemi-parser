from pydantic import BaseModel, Field
from typing import List

class LineItem(BaseModel):
    amount: float = Field(description="The total amount for this line item")
    description: str | None = Field(None, description="Description of the item or service")
    product_code: str | None = Field(None, description="Product or service code")
    quantity: int = Field(description="Quantity of items")
    unit: str | None = Field(None, description="Unit of measurement (e.g., pcs, hours)")
    unit_price: float = Field(description="Price per unit")

class VAT(BaseModel):
    amount: float = Field(description="VAT amount")
    category_code: str | None = Field(None, description="VAT category code")
    tax_amount: float | None = Field(None, description="Tax amount")
    tax_rate: float | None = Field(None, description="Tax rate as a percentage")
    total_amount: float = Field(description="Total amount including VAT")

class BankDetails(BaseModel):
    iban: str | None = Field(None, description="Bank account IBAN")
    bank_name: str | None = Field(None, description="The name of the Bank")
    beneficiary: str | None = Field(None, description="Beneficiary of the bank account or IBAN")
    swift_or_bic: str | None = Field(None, description="SWIFT code or BIC code")

class Party(BaseModel):
    name: str = Field(description="Company or individual name")
    street: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State or region")
    postal_code: str | None = Field(None, description="Postal or ZIP code")
    country: str | None = Field(None, description="Country")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    website: str | None = Field(None, description="Website URL")
    tax_id: str | None = Field(None, description="Tax identification number")
    registration: str | None = Field(None, description="Company registration number")
    bank_details: List[BankDetails] = Field(description="List of bank details in the invoice")

class Invoice(BaseModel):
    invoice_id: str = Field(description="Unique invoice identifier")
    invoice_date: str = Field(description="Invoice date in YYYY-MM-DD format")
    supplier: Party = Field(description="Information about the supplier")
    receiver: Party = Field(description="Information about the receiver")
    line_items: List[LineItem] = Field(description="List of items or services in the invoice")
    vat: List[VAT] = Field(description="VAT information")
    payment_terms: str = Field(description="Payment Terms in the invoice")