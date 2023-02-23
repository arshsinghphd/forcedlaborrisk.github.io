import streamlit as st
import pandas as pd

page_title = "Open Trade Data Pilot (Dummy)"
layout = "centered"


st.set_page_config(page_title = page_title, layout=layout)
st.title(page_title)

# -- Drop Down Menus --

years = ["2021", "2020", "2019"]
commodity = ["52 - Cotton"]

partners = pd.read_csv('C:/Users/arsha/OneDrive/LearningProgramming/LearningML/Projects/OpenTrade/Codes/partnerAreas.csv')
# source: UN Comtrade
reporters = pd.read_csv('C:/Users/arsha/OneDrive/LearningProgramming/LearningML/Projects/OpenTrade/Codes/reporterAreas.csv')
# source: UN Comtrade
areas = pd.merge(left = reporters, right = partners, on = 'id', how = 'inner')
# since 'id' 'all' is not useful, we will remove it from our list
areas = areas[areas['id'] != 'all']
areas = areas[['id', 'text_x']]
areas['id'] = areas['id'].astype(int)
areas.rename(columns={'text_x' : 'text'}, inplace=True)
areas.set_index('id', inplace = True)

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