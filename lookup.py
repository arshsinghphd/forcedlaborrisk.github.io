import countryNode
import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

def makePyvisGraph(node, pyvis_net):
    if node.name not in pyvis_net.get_nodes():
        pyvis_net.add_node(node.name, 
                            title = 'Exporter', 
                            color = node.color, 
                            size = 12)
    sum_trade = 0
    if node.imp_partners:
        for partner in node.imp_partners:
            sum_trade += partner.trade_value
            pyvis_net.add_node(partner.name, 
                            title = 'Imports {:.2f}% of {}\'s export'
                            .format(partner.trade_value, partner.parent), 
                            color = partner.color,
                            size = 12 - 2*partner.depth
                            )
            pyvis_net.add_edge(node.name, partner.name,
                        title = '{:.2f}%'.format(partner.trade_value))
            makePyvisGraph(partner, pyvis_net)
        pyvis_net.get_node(node.name)['title'] += '\n {:.2f}% of its exports go to following'.format(sum_trade)
    
    return 
    
def deep_search(reporterCode, year, comm_codes, imp_n, levels_n):
    #BLOCK 1 
    # Based on names and codes in 'areas.csv', 
    # make a dict 'areas_nodes' of node objects keyed by code.
    areas = pd.read_csv('data/areas.csv', )
    areas.rename(columns={'text_x' : 'text'}, inplace=True)
    areas.set_index('id', inplace = True)
    
    tradeMat = pd.read_csv('data/tradeMat.csv')
    tradeMat.set_index('id', inplace = True)
    tradeMat.head()

    areas_nodes = {}
    for j in tradeMat.index:
        if j == reporterCode:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'], 0, 'red')
        else:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'])
    ####
    
    #BLOCK 2
    # For level 1 iteration,
    # Start with the user provided country as the only node in 'curr_list'.
    # Make a list 'trade', of all nodes in areas_nodes it exports to.
    # While doing this sum the trade up to get 'tot_trade'.
    # Reverse sort the list 'trade', and keep only top imp_n.
    # Scan this list to add important node attributes.
    # Save these nodes as the 'next_list'.
    # 'next_list' becomes 'curr_list' for the next level iteration.
    # Iterate levels_n times.
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
                    tv = tradeMat.loc[i, str(j.code)]
                    j.trade_value = tv
                    trade.append(j)
                    tot_trade += tv
            trade.sort(key = lambda x: x.trade_value, reverse=True)
            
            trade = trade[:imp_n]
            sum_trade = 0
            counter = 0
            for partner in trade:
                counter += 1
                if partner.color == 'white':
                    sum_trade += partner.trade_value
                    partner.trade_value = 100*partner.trade_value/tot_trade
                    country.imp_partners.append(partner)
                    partner.parent = country.name
                    partner.color = 'red'
                    partner.depth = level
            country.trade_with_partners = sum_trade*100/tot_trade
            next_list.extend(country.imp_partners)
        curr_list = next_list
        level += 1
    ####
    
    # #BLOCK 3
    # # Make nx graph rooted at the user provided country node
    # nx_graph = nx.Graph()
    # makeNxGraph(areas_nodes[reporterCode], nx_graph)
    # ####
    
    #BLOCK 4
    # Make a pyvis graph from nx graph
    # save it as an html component
    pyvis_net = Network(height="700px", width="100%", 
                        bgcolor="#222222", font_color="white", 
                        directed =True)
    makePyvisGraph(areas_nodes[reporterCode], pyvis_net)
    pyvis_net.write_html("images/result.html", local=True)
    ####
    
    #BLOCK 5
    # Make excel and csv files
    table = pd.DataFrame(columns = ['a','b','export'])
    curr_list = [areas_nodes[reporterCode]]
    index = 1
    while level <= levels_n:
        for country in curr_list:
            next_list = country.imp_partners
            for partner in next_list:
                exp = str(round(partner.trade_value, 2))[:4]
                table.loc[index] = pd.Series({'a':country.name, 'b':partner.name, 'export':exp})
                index += 1
        curr_list = next_list
        level += 1
    table.loc['*'] = pd.Series({'a':'As % of total exports of B'})
    table.to_csv("images/table.xls", sep = '\t' , header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*'])
    table.to_csv("images/table.csv", sep = ',' , header = ['Exporter(A)', 'Importer(B)', 'Export(A to B)*'])
    ####
    
    return
    
    
if __name__ == '__main__':
    deep_search(reporterCode,year,comm_codes,imp_n,levels_n)
