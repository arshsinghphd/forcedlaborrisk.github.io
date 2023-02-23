import streamlit as st
import pandas as pd

page_title = "Open Trade Data Pilot (Dummy)"
layout = "centered"
icon = 'images/STREAMS-logo-v2_White_800.png'

st.set_page_config(page_title = page_title, layout=layout, page_icon = icon)
st.title(page_title)

# -- Drop Down Menus --

years = ["2021", "2020", "2019"]
commodity = ["52 - Cotton"]
areas = pd.read_csv('data/areas.csv')

# -- Input Form --

with st.form("entry_form"):
    st.write("In all of the selection boxes, you can choose from the options. You can also delete the default and start typing your choice and options will be suggested.")
    st.selectbox(f"Select Country",areas, key="reporterCode")
    col1, col2 = st.columns(2)
    col1.selectbox("Year", years, key="year")
    col2.selectbox("HS Commodity Code",commodity, key="comm_codes")
    "---"
    st.number_input(f"Define 'Important Partners' as the ones that add up to (%)", \
            min_value=5,max_value=90,format="%i",step=5,key="imp_pc")
    st.number_input("Depth: \n After your defined country, how many levels down do you want to search?", min_value=1,max_value=5,format="%i",step=1,key="levels_n")
    "---"
    submitted = st.form_submit_button()   

# --- results ---
st.header("Partnering Countries")
