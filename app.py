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

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            footer:after {
                content:'© Arsh Singh, 2022'; 
                visibility: visible;
                display: block;
                position: relative;
                #background-color: red;
                padding: 5px;
                top: 2px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -- New Users Video Demo --
video_demo_notice = st.expander("First Time? Watch Brief Video Demo Here",
                            expanded=False)
with video_demo_notice:
    video_file = open('data/demo.webm', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

# -- define functions before they are called --
@st.cache_data
def make_mat(year, comm_code, flowCode):    
    df = pd.read_csv('data/{}_{}_{}.csv'
                        .format(flowCode, comm_code, year)
                            , encoding = 'cp437')
    df = df[['ReporterCode','PartnerCode','PrimaryValue']]
    tradeMat = df.pivot(index='ReporterCode', 
                        columns='PartnerCode', values='PrimaryValue')
    tradeMat = tradeMat.fillna(0)
    tradeMat.index.name = 'id'
    ids = list(tradeMat.index)
    return tradeMat, ids
@st.cache_data
def table_to_csv(df, flowCode):
# IMPORTANT: Cache and prevent computation on every rerun
    if flowCode == 'X':
        return df.to_csv(sep = ',' , 
            header = ['Exporter(A)', 'Importer(B)', 
                                        'Export(A to B)*', 'Flag']
            ).encode('utf-8')
    elif flowCode == 'M':
        return df.to_csv(sep = ',' , 
            header = ['Importer(A)', 'Exporter(B)', 
                                        'Import(A from B)*', 'Flag']
            ).encode('utf-8')
@st.cache_data
def table_to_xls(df, flowCode):
# IMPORTANT: Cache the conversion to prevent computation on every rerun
    if flowCode == "X":
        return df.to_csv(sep = '\t' , 
            header = ['Exporter(A)', 'Importer(B)', 
                                        'Export(A to B)*', 'Flag']
            ).encode('utf-8')
    if flowCode == "M":
        return df.to_csv(sep = '\t' , 
            header = ['Importer(A)', 'Exporter(B)', 
                                        'Import(A from B)*', 'Flag']
            ).encode('utf-8')

# -- Initiate session_state vars --
def initiate_ss_vars():
    if 'reporterName_raw' not in st.session_state:
        st.session_state.reporterName_raw = '842-USA'    
    if 'year' not in st.session_state:
        st.session_state.year = 2021
    if 'comm_code_raw' not in st.session_state:
        st.session_state.comm_code_raw = '52 - Cotton'
    if 'flow' not in st.session_state:
        st.session_state.flow = 'M'
    if 'imp_n' not in st.session_state:
        st.session_state.imp_n = 2
    if 'levels_n' not in st.session_state:
        st.session_state.levels_n = 2

initiate_ss_vars()

# -- Drop Down Menu Vars --
years = ["2021", "2022"]
commodity = ["52 - Cotton"]
trade = ['Import', 'Export']


# -- Input Form --
form_notice = st.expander("Start Your Search Here",
                            expanded=False)
with form_notice:
    with st.form('form_1', clear_on_submit=False):
        col1, col2, col3= st.columns([2, 2, 2])
        comm_code_raw = col1.selectbox("HS Commodity Code",commodity)
        flow = col2.selectbox("Trade", trade)
        year = col3.selectbox("Year", years)
        submitted = st.form_submit_button()
    if submitted:
        # -- update session state var --
        st.session_state.year = year
        st.session_state.comm_code_raw = comm_code_raw
        if flow == 'Export':
            st.session_state.flow = 'X'
        else:
            st.session_state.flow = 'M'
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    # -- Drop Down Var for Area -- 
    comm_code, comm_name = re.split('-', st.session_state.comm_code_raw)
    comm_code = int(comm_code)
    flowCode = st.session_state.flow
    tradeMat, ids = make_mat(year, comm_code, flowCode)
    areas = pd.read_csv('data/areas.csv', index_col = 1)
    areas.drop('Unnamed: 0', axis = 1, inplace = True)
    areas.rename(columns={'text_x' : 'text'}, inplace=True)
    areas_codeToName = {i:areas.loc[i]['text'] for i in areas.index}
    for i in areas.index:
        areas_codeToName[i] = areas.loc[i]['text']
    list_areas = [str(i)+'-'+areas_codeToName[i] for i in tradeMat.index]
    list_areas.sort()
    if '842-USA' in list_areas:
        list_areas.remove('842-USA')
        list_areas.insert(0,'842-USA')
    reporterName_raw = st.selectbox("Country",list_areas)
    # -- update session state var --
    st.session_state.reporterName_raw = reporterName_raw  
    reporterCode, reporterName = re.split('-', st.session_state.reporterName_raw)
    reporterCode = int(reporterCode)

# -- Adjust depth and partners --
# adjust_notice = st.expander("Adjust No. of Partners and Depth Here", expanded=False)
# with adjust_notice:
    # col1, col2, col3, col4, col5, col6 = st.columns([1,4,1,1,4,1])

    # # ---- Partners ----
    # inc_p = col1.button("⊕")
    # if inc_p:
        # if st.session_state.imp_n < 10:
            # st.session_state.imp_n += 1
            
    # col2.markdown('<div style="text-align: center;">Adjust Partners</div>', unsafe_allow_html=True)

    # dec_p = col3.button("⊖")
    # if dec_p:
        # if st.session_state.imp_n > 1:
            # st.session_state.imp_n -= 1
    
    # imp_n = st.session_state.imp_n

    # # ---- Depth ----
    # inc_level = col4.button('↑')
    # if inc_level:
        # if st.session_state.levels_n < 10:
            # st.session_state.levels_n += 1
    
    # col6.markdown('<div style="text-align: center;">Adjust Depth</div>', unsafe_allow_html=True)
    
    # dec_level = col6.button('↓')
    # if dec_level:
        # if st.session_state.levels_n > 1:
            # st.session_state.levels_n -= 1
    # levels_n = st.session_state.levels_n

graph_notice = st.expander("See The Graph Here", expanded = True)
with graph_notice:
    col1, col2, col3,col4= st.columns([1,1,1,3])

    # ---- Partners ----
    inc_p = col1.button("\u2295") #circle +
    if inc_p:
        if st.session_state.imp_n < 10:
            st.session_state.imp_n += 1
    col2.markdown('<div style="text-align: left;">Partners</div>', unsafe_allow_html=True)
    dec_p = col3.button("\u2296") # circle -
    if dec_p:
        if st.session_state.imp_n > 1:
            st.session_state.imp_n -= 1
    imp_n = st.session_state.imp_n
    
    # ---- Depth ----
    inc_level = col1.button('\u2191') # arrow up
    if inc_level:
        if st.session_state.levels_n < 10:
            st.session_state.levels_n += 1
    col2.markdown("")
    col2.markdown("")
    col2.markdown('<div style="text-align: left;">Depth</div>', unsafe_allow_html=True)
    dec_level = col3.button('\u2192') # arrow down
    if dec_level:
        if st.session_state.levels_n > 1:
            st.session_state.levels_n -= 1
    levels_n = st.session_state.levels_n
    
    if flow == 'Export':
        st.markdown('#### <div style="text-align: center;"> Path of {} \
        Trade Emerging from {} in the year {}</div>'
        .format(comm_name, reporterName, year),unsafe_allow_html=True)
    else:
        st.markdown('#### <div style="text-align: center;">Path of {} \
        Trade Reaching {} in the year {}</div>'
        .format(comm_name, reporterName, year),unsafe_allow_html=True)

    #col1, col2, col3, col4, col5= st.columns([1,1,2,1,1])
    #col2.write("No. partners: \n {}".format(imp_n))
    #col4.write("Depth: \n {}".format(levels_n))
    st.write("No. partners: \n {}, Depth: \n {}".format(imp_n, levels_n))
    # -- lookup -- 
    response = lookup.deep_search(reporterCode, flowCode, 
                                        imp_n, levels_n, tradeMat, comm_name, year)

    # -- Output Area -- 
    # -- lookup.py has made an html file images/result.html --  

    HtmlFile = open("images/result.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=410, scrolling=True) 
    st.write("Depending on your search, the names in the network graph \
              below may not be legible, but you can zoom in and out. \
              You can also hold the nodes and move them around to \
              rearrange the network graph.")

node_colors_notice = st.expander("About the Color Scheme of the Nodes", expanded=False)
with node_colors_notice:
    col1, col2 = st.columns([2,8])
    #col1.markdown(<div> bg-color: rgb(255,0,0) "RED" <\div>)
    col1.write("")
    col1.write("")
    col1.markdown(f'<p style="background-color:rgb(255,0,0);\
                    color:rgb(0,0,0); text-align:center">RED</p>', 
                    unsafe_allow_html=True)
    col2.write("U. S. State Dept. reports a list of countries that have \
              a high risk of involving forced and/or child labor. Such \
              countries are colored red and labelled 'Listed'. Any \
              countries downstream a red node will also suffer a risk, \
              which is color coded in shades from pink to white.")
    col1, col2 = st.columns([2,8])
    col1.write("")
    col1.write("")
    col1.markdown(f'<p style="background-color:rgb(200,100,100);\
                    color:rgb(0,0,0);text-align:center">PINK</p>',
                    unsafe_allow_html=True)
    col1.markdown(f'<p style="background-color:rgb(200,255,255);\
                    text-align:center;color:rgb(0,0,0)">WHITE</p>',
                    unsafe_allow_html=True)
    col2.write("The color of the node for a country not in the \
                (U. S. State Dept.) list depends on the proportion \
                of its imports that come \
                from the listed countries - even the ones that \
                do not appear on the graph.")
    col2.write("**Darker the color, higher the \
                risk of involvement of forced or child labor in its \
                imports.**")

# -- table download area --
table = response[1]
xls = table_to_xls(table, flowCode)
csv = table_to_csv(table, flowCode)
download_notice = st.expander("Download Data?", expanded = False)
with download_notice:
    col1, col2, col3, col4 = st.columns([3,2,2,12]) 
    col2.download_button(".xls", xls, file_name='Table.xls', 
                       mime = 'xls')
    col3.download_button(".csv", csv, file_name='Table.csv', 
                       mime = 'csv')
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            footer:after {
                content:'© Arsh Singh, 2022'; 
                visibility: visible;
                display: block;
                position: relative;
                #background-color: red;
                padding: 5px;
                top: 2px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#st.markdown("(c) Arsh Singh, 2023", unsafe_allow_html=True)