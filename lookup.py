import countryNode

import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

listfl = ['Georgia']

def makePyvisGraph(node, pyvis_net, ncolor = 'white'):
    if node.name in listfl:
        ncolor = 'red'
        
    if node.name not in pyvis_net.get_nodes():
        pyvis_net.add_node(node.name, 
                            title = 'Exporter', 
                            color = ncolor, 
                            size = 12)
    else:
        pyvis_net.get_node(node.name)['color'] = ncolor
    sum_trade = 0
    if node.imp_partners:
        for partner in node.imp_partners:
            sum_trade += partner.trade_value
            pyvis_net.add_node(partner.name, 
                            title = 'Imports {:.2f}% of {}\'s export'
                            .format(partner.trade_value, partner.parent), 
                            color = ncolor,
                            size = 12 - 2*partner.depth
                            )
            pyvis_net.add_edge(node.name, partner.name,
                        title = '{:.2f}%'.format(partner.trade_value))
            if ncolor == "white":
                makePyvisGraph(partner, pyvis_net)
            else:
                makePyvisGraph(partner, pyvis_net, ncolor)
        pyvis_net.get_node(node.name)['title'] += \
                '\n {:.2f}% of its exports go to following'.format(sum_trade)
    
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
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'], 0)
        else:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'])
    ####
    
    #BLOCK 2: 
    # TRADE CALCULATIONS AND BULDING DATAFRAME
    # For level 1 iteration,
    # Start with the user provided country as the only node in 'curr_list'.
    # Make a list 'trade', of all nodes in areas_nodes it exports to.
    # While doing this sum the trade up to get 'tot_trade'.
    # Reverse sort the list 'trade', and keep only top imp_n.
    # Scan this list to add important node attributes.
    # Save these nodes as the 'next_list'.
    # 'next_list' becomes 'curr_list' for the next level iteration.
    # Iterate levels_n times.
    table = pd.DataFrame(columns = ['a', 'b', 'export', 'flag'])
    curr_list = [areas_nodes[reporterCode]]
    level = 1
    index = 1
    while level <= levels_n:
        next_list = []
        for country in curr_list:
            if country.code == reporterCode:
                country.engaged = True
            if country.color != 'red' and country.name in listfl:
                country.color = 'red'
            i = country.code
            trade = []
            tot_trade = 0
            for j in areas_nodes.values():
                if not j.engaged:
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
                if not partner.engaged:
                    sum_trade += partner.trade_value
                    partner.trade_value = 100*partner.trade_value/tot_trade
                    country.imp_partners.append(partner)
                    partner.parent = country.name
                    partner.color = country.color
                    partner.engaged = True
                    partner.depth = level
                    
                    flag = partner.color == 'red'
                    exp = str(round(partner.trade_value, 2))[:4]
                    table.loc[index] = pd.Series({'a':country.name, 
                                          'b':partner.name, 
                                          'export':exp,
                                          'flag': flag})
                    index += 1
            country.trade_with_partners = sum_trade*100/tot_trade
            next_list.extend(country.imp_partners)
        curr_list = next_list
        level += 1
    table.loc['*'] = pd.Series({'a':'As % of total exports of B'})
    ####
    
    #BLOCK 3
    # Make a pyvis graph and save it as an html
    
    #pyvis_net = Network(height="700px", width="100%", 
    #                    bgcolor="#222222", font_color="white", 
    #                    directed=True)
    pyvis_net = Network(height="400px", width="100%", 
                        bgcolor="#222222", font_color="white", 
                        directed=True)
    makePyvisGraph(areas_nodes[reporterCode], pyvis_net)
    pyvis_net.write_html("images/result.html", local=True)
    ####
    
    return table
    
    
if __name__ == '__main__':
    deep_search(reporterCode,year,comm_codes,imp_n,levels_n)
