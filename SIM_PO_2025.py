import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objs as go
import plotly.graph_objects as go
import re

##################################
Logo=Image.open('SIM-LOGO-02.jpg')
st.image(Logo, width=720)

#########################################################
def formatted_display0(label, value, unit):
    formatted_value = "<span style='color:yellow'>{:,.0f}</span>".format(value)
    display_text = f"{formatted_value} {unit}"
    st.write(label, display_text, unsafe_allow_html=True)

def formatted_display(label, value, unit):
    formatted_value = "<span style='color:yellow'>{:,.2f}</span>".format(value)
    display_text = f"{formatted_value} {unit}"
    st.write(label, display_text, unsafe_allow_html=True)

######################################################################
@st.cache_data
def load_po_master():
    File = "https://docs.google.com/spreadsheets/d/1dHa3wGMvEgZdkKiE8T2J9nzQmfoDTF3AnLWah-RcTWU/export?format=xlsx"
    df = pd.read_excel(File, engine='openpyxl', sheet_name='PO_Master')
    return df

@st.cache_data
def load_logistic():
    File = "https://docs.google.com/spreadsheets/d/1UwN0kCwAPFmU0vNtrliHjazWbyxWT04fqNWatF7O6sI/export?format=xlsx"
    df = pd.read_excel(File, engine='openpyxl')
    return df

# Load data
po_master_df = load_po_master()
logistic_df = load_logistic()

# st.subheader("📦 PO_Master Data")
# st.dataframe(po_master_df)

# st.subheader("🚚 Logistic Data")
# st.dataframe(logistic_df)

#########################################################
# Clean function
def extract_po_no(text):
    if pd.isna(text):
        return ''
    parts = re.split(r'\|', str(text))
    return parts[0].strip()

def clean_text(text):
    if pd.isna(text):
        return ''
    return re.sub(r'\s+', '', str(text)).strip()

# Extract PO_No from logistic_df
logistic_df['PO_No'] = logistic_df['PO ID'].apply(extract_po_no)

# Clean both PO ID fields
po_master_df['PO ID'] = po_master_df['PO ID'].apply(clean_text)
logistic_df['PO_No'] = logistic_df['PO_No'].apply(clean_text)

#########################################################
# Reduce logistic columns
logistic_df = logistic_df[['PO_No', 'Logistic Status', 'Production Completed Date', 'ETD-Date', 'Logistic Remark']]
logistic_df.rename(columns={'Production Completed Date': 'FG-Date'}, inplace=True)

# Merge PO
PO_Tracker = pd.merge(po_master_df, logistic_df, left_on='PO ID', right_on='PO_No', how='left')

# Debug: show unmatched PO
unmatched = po_master_df[~po_master_df['PO ID'].isin(logistic_df['PO_No'])]
# if not unmatched.empty:
#     st.subheader("⚠️ PO ID Not Matched with Logistic")
#     # st.dataframe(unmatched[['PO ID']])

# Continue with cleaned + merged data
PO_Tracker = PO_Tracker[['PO ID', 'PO_No', 'Customer', 'Other-Customer Name', 'Part-Name', 'Product',
                         'PO-Qty', 'Customer-ETA-Date', 'Logistic Status', 'FG-Date', 'ETD-Date', 'Logistic Remark']]
PO_Tracker.index += 1

# Convert dates
PO_Tracker['FG-Date'] = pd.to_datetime(PO_Tracker['FG-Date'], errors='coerce').dt.date
PO_Tracker['ETD-Date'] = pd.to_datetime(PO_Tracker['ETD-Date'], errors='coerce').dt.date
PO_Tracker['Customer-ETA-Date'] = pd.to_datetime(PO_Tracker['Customer-ETA-Date'], errors='coerce').dt.date

# Replace Customer name
PO_Tracker['Customer'] = np.where(
    PO_Tracker['Customer'] == 'Other-Customer',
    PO_Tracker['Other-Customer Name'],
    PO_Tracker['Customer']
)

# Format PO-Qty
PO_Tracker['PO-Qty'] = pd.to_numeric(PO_Tracker['PO-Qty'], errors='coerce').fillna(0)
PO_Tracker['PO-Qty'] = PO_Tracker['PO-Qty'].apply(lambda x: f"{x:,.0f}")

# Final columns
PO_Tracker = PO_Tracker[['PO ID', 'PO_No', 'Customer', 'Part-Name', 'Product', 'PO-Qty',
                         'Customer-ETA-Date', 'Logistic Status', 'FG-Date', 'ETD-Date', 'Logistic Remark']]

st.subheader("📋 PO Tracker")
st.dataframe(PO_Tracker)

# Summary
st.write('---')
st.write('**PO Summarize**')
TT_PO = PO_Tracker['Product'].count()
TT_MASS = PO_Tracker['Product'].str.contains('MASS-Part', na=False).sum()
TT_Mold = PO_Tracker['Product'].str.contains('Mold', na=False).sum()
TT_STB = PO_Tracker['Product'].str.contains('Steel', na=False).sum()
formatted_display0('Total PO AMT: ', TT_PO, 'Unit')
formatted_display0('Total MASS PO AMT: ', TT_MASS, 'Unit')
formatted_display0('Total Mold PO AMT: ', TT_Mold, 'Unit')
formatted_display0('Total Steel Bush PO AMT: ', TT_STB, 'Unit')
st.write('---')

# ETA Filter by Month
month_map = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}
year = 2025
Month_Selected = st.selectbox('Select Customer ETA', list(month_map.keys())[5:])  # Jun-Dec
month_num = int(month_map[Month_Selected])

filtered_df = PO_Tracker[
    (PO_Tracker['Customer-ETA-Date'].apply(lambda d: d.year if pd.notna(d) else 0) == year) &
    (PO_Tracker['Customer-ETA-Date'].apply(lambda d: d.month if pd.notna(d) else 0) == month_num)
]

st.write(f"Showing ETA for **{Month_Selected} {year}**:")
filtered_df = filtered_df.reset_index(drop=True)
filtered_df.index += 1
filtered_df['Customer-ETA-Date'] = pd.to_datetime(filtered_df['Customer-ETA-Date']).dt.date
filtered_df = filtered_df[['PO ID', 'Customer', 'Part-Name', 'Product', 'PO-Qty',
                           'Customer-ETA-Date', 'Logistic Status', 'ETD-Date']]
st.dataframe(filtered_df)
