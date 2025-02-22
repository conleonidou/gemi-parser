### Gemini 2.0 Flash Parser for Invoices Documentation
#### Overview
The Gemini 2.0 Flash Parser is a tool designed to parse invoices. It is available as a [Streamlit App](https://gemi-parser.streamlit.app/).

#### Important Notice
**Use with Caution**: This application is provided as-is, and users are advised to exercise caution when utilizing it, especially with sensitive or confidential data.

#### Library Information
This application is built using [Streamlit](https://streamlit.io/), a Python library that allows for the creation of web apps for data science and machine learning in a simple and straightforward way. To use Streamlit, you will need to have Python installed on your system. You can install Streamlit using pip:
```bash
pip install streamlit
```
The Gemini 2.0 Flash Parser also relies on the following dependencies:
* `pandas` for data manipulation and analysis
* `numpy` for numerical computations

You can install these dependencies using pip:
```bash
pip install pandas numpy
```
Here's an example of how to use these libraries:
```python
import pandas as pd
import numpy as np
import streamlit as st

# Create a sample DataFrame
data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
        'Age': [28, 24, 35, 32],
        'Country': ['USA', 'UK', 'Australia', 'Germany']}
df = pd.DataFrame(data)

# Display the DataFrame
st.write(df)

# Perform numerical computations
array = np.array([1, 2, 3, 4, 5])
st.write(np.mean(array))
```
#### Configuration Options
The Gemini 2.0 Flash Parser can be configured to parse invoices in different formats. The following options are available:
* `invoice_format`: specifies the format of the invoice (e.g. PDF, CSV, etc.)
* `output_format`: specifies the format of the output (e.g. CSV, JSON, etc.)

You can configure these options by passing them as arguments to the `parse_invoice` function. For example:
```python
import streamlit as st

st.parse_invoice(invoice_format="PDF", output_format="CSV")
```
#### Getting Started
To use the Gemini 2.0 Flash Parser, simply navigate to the [Streamlit App URL](https://gemi-parser.streamlit.app/)