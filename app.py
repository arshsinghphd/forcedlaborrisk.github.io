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
trade = ['Export', 'Import', 'Both']
areas = pd.read_csv('data/areas.csv')
areas['name'] = areas['id'].astype(str)+ '-' + areas['text_x']
areas = areas.set_index('id')
areas = areas.rename(columns={'name' : 'text'})
areas = areas[['text']]
max_partners = 10
max_levels = 10

# -- Initiate session_state vars --
if 'reporterName_raw' not in st.session_state:
    st.session_state.reporterName_raw = '4-Afghanistan'    
if 'year' not in st.session_state:
    st.session_state.year = 2021
if 'comm_code_raw' not in st.session_state:
    st.session_state.comm_code_raw = '52 - Cotton'
if 'imp_n' not in st.session_state:
    st.session_state.imp_n = 1
if 'levels_n' not in st.session_state:
    st.session_state.levels_n = 1

# -- Input Form --
with st.form("entry_form", clear_on_submit=False):
    st.write("In all of the selection boxes, you can choose from the options or you can also delete the default and start typing your choice and options will be suggested.")
    st.write("For *No. Trade Partners*, the largest trade values are chosen first.")
    st.write("For *Depth of the Search*, After your defined country, how many levels down do you want to search?")
    
    col1, col2, col3 = st.columns(3)
    reporterName_raw = col1.selectbox(f"Select Country",areas)
    comm_code_raw = col2.selectbox("HS Commodity Code",commodity)
    trade = col3.selectbox("Trade", trade)
    year = col1.selectbox("Year", years)
    imp_n = col2.number_input("No. Trade Partners", \
                            min_value=1,max_value=10,format="%i",step=1)
    levels_n = col3.number_input("Depth of the Search", \
                            min_value=1, max_value=10,format="%i",step=1)
    
    dataDown = ''
    "---"
    submitted = st.form_submit_button()

# -- Based on Submission, update sesion_state variables --
if submitted:
    st.session_state.reporterName_raw = reporterName_raw    
    st.session_state.year = int(year)
    st.session_state.comm_code_raw = comm_code_raw
    st.session_state.imp_n = imp_n
    st.session_state.levels_n = levels_n


# -- define functions before they are called --
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

# -- Output Area --
reporterName = re.split('-', st.session_state.reporterName_raw)[1]
st.markdown("#### Current Values")
st.write("County: {}".format(reporterName))
st.write("Year: {}".format(year))
st.write("The number of trade partners of each node country: {}.".format(imp_n))
st.write("Search {} level(s) deep".format(levels_n))
st.write("Depending on your search, the names in the network graph below may not be legible, but you can zoom in and out. You can also hold the nodes and move them around to rearrange the map.")
comm_name = re.split('-',st.session_state.comm_code_raw)[1]
st.write("Red colored nodes: U. S. State Dept. reports that {} grown and processed in that country to have high risk of involving forced and/or child labor. Any countries downstream a red node will also suffer the same risk.".format(comm_name))

"---"

st.header("Partnering Countries")
# -- Adjust depth and partners --
col1, col2= st.columns(2)
col1.write('Adjust Levels')
col2.write('Adjust Partners')
col1, col2, col3, col4 = st.columns(4)
# ---- Depth ----
inc_level = col1.button('+1 Level')
if inc_level:
    if st.session_state.levels_n < 10:
        st.session_state.levels_n += 1
dec_level = col2.button('-1 Level')
if dec_level:
    if st.session_state.levels_n > 1:
        st.session_state.levels_n -= 1
levels_n = st.session_state.levels_n
st.write("Search {} level(s) deep".format(levels_n))
# ---- Partners ----
inc_part = col3.button('+1 Partner')
if inc_part:
    if st.session_state.imp_n < 10:
        st.session_state.imp_n += 1
dec_p = col4.button('-1 Partner')
if dec_p:
    if st.session_state.imp_n > 1:
        st.session_state.imp_n -= 1
imp_n = st.session_state.imp_n
st.write("The number of trade partners of each node country: {}.".format(imp_n))


# -- lookup --
#st.write(st.session_state)
reporterCode = int(re.split('-', st.session_state.reporterName_raw)[0])
year = st.session_state.year
comm_code = int(re.split('-', st.session_state.comm_code_raw)[0])
levels_n = st.session_state.levels_n # redundant but easy to read
imp_n = st.session_state.imp_n # redundant but easy to read

if imp_n**(levels_n + 1) > len(areas):
    "---"
    st.write("Your current selection results in too many countires.\n Please refine your search criteria by adjusting partners or levels.")
else:
    # -- call lookup.py --         
    table = lookup.deep_search(reporterCode, year, 
                                comm_code, imp_n, levels_n)
    # -- lookup.py has made an html file images/result.html --        
    HtmlFile = open("images/result.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=410, scrolling=True)
    # -- table download area --
    "---"
    dataDown = st.radio("Would you like to download the underlying data as a file?",('No','Excel', 'CSV'))        
    csv = table_to_csv(table)
    xls = table_to_xls(table)
    if dataDown == 'Excel':
        st.download_button("Download Excel", xls, file_name='Table.xls', mime = 'xls', help = "Download file, may move the graph nodes around")
    if dataDown == 'CSV':
        st.download_button("Download CSV", csv, file_name='Table.csv', mime = 'csv', help = "Download file, may move the graph nodes around")
