import lookup

import math
import numpy as np
import pandas as pd
from PIL import Image
import re
import streamlit as st
import streamlit.components.v1 as components



page_title = "Open Trade Data Pilot"
layout = "centered"
icon = 'images/STREAMS-logo-v2_White_800.png'
st.set_page_config(page_title = page_title, layout=layout, page_icon = icon)

# -- Logo and Title--
logo = Image.open('images/Verite-Wordmark-Web-Small-2.jpg')
col1, col2 = st.columns([1, 4])
col1.image(logo)
col2.title(page_title)

# -- Drop Down Menu Vars --
#years = ["2022", "2021", "2020", "2019"]
years = ["2021", "2022"]
commodity = ["52 - Cotton"]
#trade = ['Export', 'Import', 'Both']
trade = ['Import', 'Export']
areas = pd.read_csv('data/areas.csv')
areas['name'] = areas['id'].astype(str)+ '-' + areas['text_x']
areas = areas.set_index('id')
areas = areas.rename(columns={'name' : 'text'})

list_areas = ['842-USA']
for country in areas['text']:
    if country != '842-USA':
        list_areas.append(country)
        
# -- Initiate session_state vars --
if 'reporterName_raw' not in st.session_state:
    st.session_state.reporterName_raw = '842-USA'    
if 'year' not in st.session_state:
    st.session_state.year = 2021
if 'comm_code_raw' not in st.session_state:
    st.session_state.comm_code_raw = '52 - Cotton'
if 'flow' not in st.session_state:
    st.session_state.flow = "M"
if 'imp_n' not in st.session_state:
    st.session_state.imp_n = 2
if 'levels_n' not in st.session_state:
    st.session_state.levels_n = 2

# -- Input Form --
with st.form("entry_form", clear_on_submit=False):
    st.write("In all of the selection boxes, you can choose from the options or you can also delete the default and start typing your choice and options will be suggested.")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    reporterName_raw = col1.selectbox(f"Select Country",list_areas)
    comm_code_raw = col2.selectbox("HS Commodity Code",commodity)
    flow = col3.selectbox("Trade", trade)
    year = col4.selectbox("Year", years)
    dataDown = ''
    submitted = st.form_submit_button()

# -- Based on Submission, update sesion_state variables --
if submitted:
    st.session_state.reporterName_raw = reporterName_raw    
    st.session_state.year = int(year)
    st.session_state.comm_code_raw = comm_code_raw
    if flow == "Export":
        st.session_state.flow = "X"
    elif flow == "Import":
        st.session_state.flow = "M"
    else:
        st.session_state.flow = "B"

# -- define functions before they are called --
@st.cache_data
def table_to_csv(df, flowCode):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    if flowCode == 'X':
        return df.to_csv(sep = ',' , 
            header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*', 'Flag']
            ).encode('utf-8')
    elif flowCode == 'M':
        return df.to_csv(sep = ',' , 
            header = ['Importer(A)', 'Exporter(B)', 'Import(A from B)*', 'Flag']
            ).encode('utf-8')
@st.cache_data
def table_to_xls(df, flowCode):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    if flowCode == "X":
        return df.to_csv(sep = '\t' , 
            header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*', 'Flag']
            ).encode('utf-8')
    if flowCode == "M":
        return df.to_csv(sep = '\t' , 
            header = ['Importer(A)', 'Exporter(B)', 'Import(A from B)*', 'Flag']
            ).encode('utf-8')

@st.cache_data
def make_mat(year, comm_code, flowCode):
    try:
        tradeMat = pd.read_csv('data/tradeMat_{}_{}_{}.csv'.format(year, comm_code, flowCode))
        df = pd.read_csv('data/{}_{}_{}.csv'.format(flowCode, comm_code, year), encoding = 'cp437')
        df = df[['ReporterCode','PartnerCode','PrimaryValue']]
        ids = list(df['ReporterCode'].unique())
    except:
        df = pd.read_csv('data/{}_{}_{}.csv'.format(flowCode, comm_code, year), encoding = 'cp437')
        df = df[['ReporterCode','PartnerCode','PrimaryValue']]
        ids = list(df['ReporterCode'].unique())
        temp = np.zeros(shape=(len(ids),len(ids)), dtype = 'int64')
        for i in range(len(ids)):
            for j in range(len(ids)):
                if i == j:
                    temp[i][j] = 0
                else:
                    try:
                        temp[i][j] = df[df['ReporterCode'] == ids[i]][df['PartnerCode'] == ids[j]]['PrimaryValue']/10**6
                    except:
                        temp[i][j] = 0
        tradeMat = pd.DataFrame(temp)
        tradeMat.index.name = 'id'
        colsToIds = {}
        for i, j in zip(range(0, len(ids)), ids):
            colsToIds[i] = j
        tradeMat.rename(colsToIds, inplace = True)
        tradeMat.rename(columns = colsToIds, inplace = True)
        tradeMat = tradeMat.astype(int)
        # a = list(df['ReporterCode'])
        # b = list(df['PartnerCode'])
        # all_ids = list(pd.DataFrame(a+b)[0].unique())
        tradeMat.to_csv('data/tradeMat_{}_{}_{}.csv'.format(year, comm_code, flowCode))
    return tradeMat, ids
    
# -- Output Area --
reporterName = re.split('-', st.session_state.reporterName_raw)[1]
comm_name = re.split('-',st.session_state.comm_code_raw)[1]
st.markdown("#### Current Values")
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
col1.write("{}".format(reporterName))
col2.write("{}".format(comm_name))
col3.write("{}".format(flow))
col4.write("{}".format(year))
st.write("Depending on your search, the names in the network graph below may not be legible, but you can zoom in and out. You can also hold the nodes and move them around to rearrange the network graph.")
st.write("Red colored nodes: U. S. State Dept. reports that {} grown and processed in that country to have high risk of involving forced and/or child labor. Any countries downstream a red node will also suffer the same risk.".format(comm_name))
"---"
if flow == 'Export':
    st.markdown('#### <div style="text-align: center;"> Path of {} Trade Emerging from {} in {}</div>'.format(comm_name, reporterName, year),unsafe_allow_html=True)
elif flow == 'Import':
    st.markdown('#### <div style="text-align: center;">Path of {} Trade Reaching {} in {}</div>'.format(comm_name, reporterName, year),unsafe_allow_html=True)
else:
    st.markdown('#### <div style="text-align: center;">Path of {} Trade Centered at {} in {}</div>'.format(comm_name, reporterName, year),unsafe_allow_html=True)

# -- Adjust depth and partners --
col1, col2= st.columns(2)
col1.markdown('<div style="text-align: center;">Adjust Partners</div>', unsafe_allow_html=True)
col2.markdown('<div style="text-align: center;">Adjust Levels</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(12)

# ---- Partners ----
inc_part = col2.button('⊕')
if inc_part:
    if st.session_state.imp_n < 10:
        st.session_state.imp_n += 1
dec_p = col5.button('⊖')
if dec_p:
    if st.session_state.imp_n > 1:
        st.session_state.imp_n -= 1
imp_n = st.session_state.imp_n

# ---- Depth ----
inc_level = col8.button('↑')
if inc_level:
    if st.session_state.levels_n < 10:
        st.session_state.levels_n += 1
dec_level = col11.button('↓')
if dec_level:
    if st.session_state.levels_n > 1:
        st.session_state.levels_n -= 1
levels_n = st.session_state.levels_n
col1, col2= st.columns(2)
col1.write("No. Imp. trade partners: {}.".format(imp_n))
col2.write("Search {} level(s) deep".format(levels_n))

# -- lookup --
#st.write(st.session_state)
reporterCode = int(re.split('-', st.session_state.reporterName_raw)[0])
year = st.session_state.year
comm_code = int(re.split('-', st.session_state.comm_code_raw)[0])
flowCode = st.session_state.flow
levels_n = st.session_state.levels_n # redundant but easy to read
imp_n = st.session_state.imp_n # redundant but easy to read
tradeMat, ids = make_mat(year, comm_code, flowCode)
st.session_state.tradeMat = tradeMat

if reporterCode in ids:
    # -- call lookup.py --         
    response = lookup.deep_search(reporterCode, flowCode, 
                                    imp_n, levels_n, tradeMat)
else: 
    response = (False,)

if response[0]:
    # -- lookup.py has made an html file images/result.html --        
    HtmlFile = open("images/result.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=410, scrolling=True)
    "---"
    # -- table download area --
    dataDown = st.radio("Would you like to download the underlying data as a file?",('No','Excel', 'CSV'))  
    table = response[1]
    csv = table_to_csv(table, flowCode)
    xls = table_to_xls(table, flowCode)
    if dataDown == 'Excel':
        st.download_button("Download Excel", xls, file_name='Table.xls', mime = 'xls', help = "Download file, may move the graph nodes around")
    if dataDown == 'CSV':
        st.download_button("Download CSV", csv, file_name='Table.csv', mime = 'csv', help = "Download file, may move the graph nodes around")
else:
    st.write('There is no data for the trade of {} from/to {}'.format(comm_name,reporterName))