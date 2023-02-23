import streamlit as st
import pandas as pd
import requests 
import time
import node

def printNodes(country):
    st.write('--------------------------\|'*country.depth, country.name)
    if len(country.imp_partners) == 0:
        return
    for partner in country.imp_partners:
        printNodes(partner)
    
def deep_search(reporterCode, year, comm_codes, imp_pc, levels_n):
    areas = pd.read_csv('data/areas.csv', )
    areas.rename(columns={'text_x' : 'text'}, inplace=True)
    areas.set_index('id', inplace = True)
    Type_CS = "C"
    Freq_AM = "A"
    clCode = "HS"
    
    tradeMat = pd.read_csv('data/tradeMat.csv')
    tradeMat.set_index('id', inplace = True)
    tradeMat.head()
    
    areas_nodes = {}
    for j in tradeMat.index:
        if j == reporterCode:
            if j not in areas_nodes.keys():
                areas_nodes[j] = node.node(j, areas.loc[j]['text'], 0, 'red')
        else:
            if j not in areas_nodes.keys():
                areas_nodes[j] = node.node(j, areas.loc[j]['text'])
                
    curr_list = [areas_nodes[reporterCode]]

    level = 1
    while level <= levels_n:
        next_list = []
        for country in curr_list:
            i = country.code
            trade = []
            tot_trade = 0
            for j in areas_nodes.values():
                if j.color == 'white':
                    trade_value = tradeMat.loc[i, str(j.code)]
                    j.trade_value = trade_value 
                    trade.append(j)
                    tot_trade += trade_value
            trade.sort(key = lambda x: x.trade_value, reverse=True)
            
            sum_trade = 0
            for partner in trade:
                if sum_trade < (imp_pc * tot_trade/100):
                    if partner.color == 'white':
                        sum_trade += partner.trade_value
                        partner.trade_value = 0
                        country.imp_partners.append(partner)
                        partner.parent_code = i
                        partner.color = 'red'
                        partner.depth = level
            next_list.extend(country.imp_partners)
        curr_list = next_list
        level += 1
        
    printNodes(areas_nodes[reporterCode])
    
if __name__ == '__main__':
    deep_search(reporterCode,year,comm_codes,imp_pc,levels_n)
