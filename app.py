import streamlit as st
import pandas as pd
from PIL import Image
import lookup
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
    year = col1.selectbox("Year", years)
    comm_code_raw = col2.selectbox("HS Commodity Code",commodity)
    comm_code = int(re.split('-',comm_code_raw)[0])
    comm_name = re.split('-',comm_code_raw)[1]
    "---"
    imp_pc = st.number_input(f"Define 'Important Partners' as the ones that add up to (%)", \
            min_value=5,max_value=90,format="%i",step=5)
    levels_n = st.number_input("Depth: \n After your defined country, how many levels down do you want to search?", min_value=1,max_value=5,format="%i",step=1)
    "---"
    submitted = st.form_submit_button()   


# --- Output Area ---
st.header("Partnering Countries")

# -- Looking up --
if submitted:
    # fix commodity code with regex later
    year = int(year)
    imp_pc = int(imp_pc)
    levels_n = int(levels_n)
    
    st.write("You selected the following values.")
    st.write("County: {}".format(reporterName))
    st.write("Year: {}".format(year))
    st.write("Define Important partners as the countries that make up {}% of the exports of {}.".format(imp_pc, comm_name))
    st.write("Search {} level(s) deep".format(levels_n))
    "---"
    st.write("Result")
    # for now overwriting commodity code as integer 52
    comm_code = 52
    lookup.deep_search(reporterCode, year, comm_code, imp_pc, levels_n)
