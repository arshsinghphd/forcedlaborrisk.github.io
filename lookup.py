import node

import networkx as nx
import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

# def makeNxGraph(node, nx_graph):
    # nx_graph.add_node(node.code, label = node.name)
    # if node.imp_partners:
        # for partner in node.imp_partners:
            # nx_graph.add_node(partner.code, label = partner.name)
            # nx_graph.add_edge(node.code, partner.code)
            # makeNxGraph(partner, nx_graph)
    # return 
    
def makeNxGraph(node, nx_graph):
    nx_graph.add_node(node.name, val = node.code)
    if node.imp_partners:
        for partner in node.imp_partners:
            nx_graph.add_node(partner.name, val = partner.code)
            nx_graph.add_edge(node.name, partner.name)
            makeNxGraph(partner, nx_graph)
    return
    
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
    nx_graph = nx.Graph()
    makeNxGraph(areas_nodes[reporterCode], nx_graph)
    pyvis_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    pyvis_net.from_nx(nx_graph)
    pyvis_net.write_html("images/result.html")
    nx.write_graphml_lxml(nx_graph,  "images/result2.graphml")
    return
    
    
if __name__ == '__main__':
    deep_search(reporterCode,year,comm_codes,imp_pc,levels_n)
