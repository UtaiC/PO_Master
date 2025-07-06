import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objs as go
import plotly.graph_objects as go
import locale

##################################
Logo=Image.open('SIM-LOGO-02.jpg')
st.image(Logo,width=720)
#########################################################
def formatted_display0(label, value, unit):
    formatted_value = "<span style='color:yellow'>{:,.0f}</span>".format(value)  # Format value with comma separator and apply green color
    display_text = f"{formatted_value} {unit}"  # Combine formatted value and unit
    st.write(label, display_text, unsafe_allow_html=True)
######################################################
def formatted_display(label, value, unit):
    formatted_value = "<span style='color:yellow'>{:,.2f}</span>".format(value)  # Format value with comma separator and apply green color
    display_text = f"{formatted_value} {unit}"  # Combine formatted value and unit
    st.write(label, display_text, unsafe_allow_html=True)
# ######################################################
# month_map = {
#     'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
#     'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
#     'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
# }
# #########
# year = 2025
# Month_Selected = st.selectbox('Customer ETA', ['Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
# month_num = int(month_map[Month_Selected])

##############################################################################################################################################

@st.cache_data
def load_po_master():
    File = "https://docs.google.com/spreadsheets/d/1dHa3wGMvEgZdkKiE8T2J9nzQmfoDTF3AnLWah-RcTWU/export?format=xlsx"
    
    # Load only the 'OP_Master' sheet
    df = pd.read_excel(File, engine='openpyxl', sheet_name='PO_Master')
    return df

# Load the data
po_master_df = load_po_master()

# Show in Streamlit
st.subheader("PO_Master Data")
# st.dataframe(po_master_df)

##############################################################################################################################################################
@st.cache_data
def load_logistic():
    File = "https://docs.google.com/spreadsheets/d/1UwN0kCwAPFmU0vNtrliHjazWbyxWT04fqNWatF7O6sI/export?format=xlsx"
    
    # Load only the 'OP_Master' sheet
    df = pd.read_excel(File, engine='openpyxl')
    return df

# Load the data
logistic_df = load_logistic()

# Show in Streamlit
# st.subheader("Logistic Data")
# st.dataframe(logistic_df)
#################################################
logistic_df['PO_No'] = logistic_df['PO ID'].str.split('|').str[0].str.strip()
logistic_df=logistic_df[['PO_No','Logistic Status','Production Completed Date','ETD-Date','Logistic Remark']]
logistic_df.rename(columns={'Production Completed Date': 'FG-Date'}, inplace=True)
# logistic_df[['PO_No','Logistic Status','FG-Date','ETD-Date']]
#################################################
PO_Tracker= pd.merge(po_master_df, logistic_df,left_on='PO ID',right_on='PO_No', how='left')
PO_Tracker=PO_Tracker[['PO ID','Customer','Other-Customer Name','Part-Name','Product','PO-Qty','Customer-ETA-Date','Logistic Status','FG-Date','ETD-Date','Logistic Remark']]
PO_Tracker.index = PO_Tracker.index+1
PO_Tracker['FG-Date'] = pd.to_datetime(PO_Tracker['FG-Date']).dt.date
PO_Tracker['ETD-Date'] = pd.to_datetime(PO_Tracker['ETD-Date']).dt.date
PO_Tracke=PO_Tracker['Customer-ETA-Date'] = pd.to_datetime(PO_Tracker['Customer-ETA-Date']).dt.date

PO_Tracker['Customer']= np.where(
    PO_Tracker['Customer'] == 'Other-Customer',
    PO_Tracker['Other-Customer Name'],
    PO_Tracker['Customer']
)
################
PO_Tracker['PO-Qty']=PO_Tracker['PO-Qty'] = pd.to_numeric(PO_Tracker['PO-Qty'], errors='coerce').fillna(0)
def format_quantity_full(qty):
    if pd.isna(qty): # Handle NaN or non-numeric values
        return ""
    # Format with comma separator and no decimal places
    return f"{qty:,.0f}"
PO_Tracker['PO-Qty']=PO_Tracker['PO-Qty'].apply(format_quantity_full)
#################

PO_Tracker=PO_Tracker[['PO ID','Customer','Part-Name','Product','PO-Qty','Customer-ETA-Date','Logistic Status','FG-Date','ETD-Date','Logistic Remark']]
st.dataframe(PO_Tracker)
st.write('---')
st.write('**PO Summarize**')
TT_PO = PO_Tracker['Product'].count()
TT_MASS = PO_Tracker['Product'].str.contains('MASS-Part', na=False).sum()
TT_Mold = PO_Tracker['Product'].str.contains('Mold', na=False).sum()
TT_STB = PO_Tracker['Product'].str.contains('Steel', na=False).sum()
formatted_display0('Total PO AMT: ',round(TT_PO),'Unit')
formatted_display0('Total MASS PO AMT: ',round(TT_MASS),'Unit')
formatted_display0('Total Mold PO AMT: ',round(TT_Mold),'Unit')
formatted_display0('Total Steel Bush PO AMT: ',round(TT_STB),'Unit')
st.write('---')
################ Select Month #################
PO_Tracker['Customer-ETA-Date'] = pd.to_datetime(PO_Tracker['Customer-ETA-Date'], errors='coerce')
############################################
year = 2025
month_map = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}
Month_Selected = st.selectbox('Select Customer ETA', ['Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
month_num = int(month_map[Month_Selected])
filtered_df = PO_Tracker[
    (PO_Tracker['Customer-ETA-Date'].dt.year == year) &
    (PO_Tracker['Customer-ETA-Date'].dt.month == month_num)
]
#################################################
st.write(f"Showing ETA for {Month_Selected} {year}:")
filtered_df = filtered_df.reset_index(drop=True) 
filtered_df.index += 1 
filtered_df['Customer-ETA-Date']=filtered_df['Customer-ETA-Date'] = pd.to_datetime(filtered_df['Customer-ETA-Date']).dt.date
filtered_df=filtered_df[['PO ID','Customer','Part-Name','Product','PO-Qty','Customer-ETA-Date','Logistic Status','ETD-Date']]
st.dataframe(filtered_df)
