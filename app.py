import lookup
import math
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from PIL import Image
import re

page_title = "Open Trade Data Pilot (Dummy)"
layout = "centered"
icon = 'images/STREAMS-logo-v2_White_800.png'


st.set_page_config(page_title = page_title, layout=layout, page_icon = icon)
st.title(page_title)

# -- Logo --
logo = Image.open('images/Verite-Wordmark-Web-Small-2.jpg')
st.image(logo)

# -- Drop Down Menus --

years = ["2021", "2020", "2019"]
commodity = ["52 - Cotton"]
trade = ['Import', 'Export', 'Both']
areas = pd.read_csv('data/areas.csv')
areas['name'] = areas['id'].astype(str)+ '-' + areas['text_x']
areas = areas.set_index('id')
areas = areas.rename(columns={'name' : 'text'})
areas = areas[['text']]
# -- Input Form --

with st.form("entry_form", clear_on_submit=False):
    st.write("In all of the selection boxes, you can choose from the options. You can also delete the default and start typing your choice and options will be suggested.")
    reporterName = st.selectbox(f"Select Country",areas)
    reporterCode = int(re.split('-',reporterName)[0])
    reporterName = re.split('-',reporterName)[1]
    col1, col2 = st.columns(2)
    trade = col1.selectbox("Trade", trade)
    year = col1.selectbox("Year", years)
    comm_code_raw = col2.selectbox("HS Commodity Code",commodity)
    comm_code = int(re.split('-',comm_code_raw)[0])
    comm_name = re.split('-',comm_code_raw)[1]
    "---"
    imp_n = st.number_input(f"Enter the number max number of trade partners.\nPartners with the largest trade values are chosen first.", \
            min_value=1,max_value=10,format="%i",step=1)
    levels_n = st.number_input("Depth: \n After your defined country, how many levels down do you want to search?", \
    min_value=1, max_value= 5,format="%i",step=1)
    dataDown = ''
    "---"
    submitted = st.form_submit_button()
# --- Output Area ---
if submitted:
    # fix commodity code with regex later
    year = int(year)
    imp_n = int(imp_n)
    levels_n = int(levels_n)
    st.write("You selected the following values.")
    st.write("County: {}".format(reporterName))
    st.write("Year: {}".format(year))
    st.write("The max number of trade partners of each node country: {}".format(imp_n))
    st.write("Search {} level(s) deep".format(levels_n))
    "---"

# for now overwriting commodity code as integer 52
comm_code = 52

@st.cache_data
def table_to_csv(df):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep = ',' , 
         header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*', 'Flag']
         ).encode('utf-8')

@st.cache_data
def table_to_xls(df):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep = '\t' , 
         header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*', 'Flag']
         ).encode('utf-8')

# -- call the code --
if imp_n**(levels_n + 1) > len(areas):
        st.write("Your current selection results in too many countires. Please refine your search criteria by reducing partners or levels.")
else:
    table = lookup.deep_search(reporterCode, year, comm_code, imp_n, levels_n)
    # -- code has made an html file images/result.html --
    st.header("Partnering Countries")
    st.write("Depending on your search, the names in the network graph below may not be legible, but you can zoom in and out. You can also hold the nodes and move them around to rearrange the map.")
    st.write("Red colored nodes: U. S. State dept. reports that {} grown and processed in that country to have high risk of involving forced or child labor. Any countries downstream a red node will also suffer the same risk.".format(comm_name))
    HtmlFile = open("images/result.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=710, scrolling=True)
    dataDown = st.radio("Would you like to download the underlying data as a file?",('No','Excel', 'CSV'))    
        
    csv = table_to_csv(table)
    xls = table_to_xls(table)
        
    if dataDown == 'Excel':
        st.download_button("Download Excel", xls, file_name='Table.xls', mime = 'xls', help = "Download file, may move the graph nodes around")
    if dataDown == 'CSV':
        st.download_button("Download CSV", csv, file_name='Table.csv', mime = 'csv', help = "Download file, may move the graph nodes around")

# reset the image/result.html to default numbers    
lookup.deep_search(reporterCode, year, comm_code, imp_n, 1)