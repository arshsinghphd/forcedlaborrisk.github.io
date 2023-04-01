import countryNode  

from collections import deque
import numpy as np
import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

listfl = list(pd.read_csv('data/listfl_cotton.csv')['0'])

def makePyvisGraph(node, pyvis_net, flowCode, levels_n, imp_n, tradeMat):
    nodes_q = deque()
    partners_q = deque()
    level = 0
    key = 0
    
    curr_list = deque()
    curr_list.append(node)
    
    while level <= levels_n:
        next_list = deque()
        while curr_list:
            node = curr_list.pop()
            if node.imp_partners:
                next_list.extendleft(node.imp_partners)            
            # choose key
            if pyvis_net.get_nodes():
                key = max(pyvis_net.get_nodes()) + 1
                pyvis_net.add_node(key, label = node.name, 
                    color = node.color, title = node.name, 
                    shape = 'box', value = node.code)
            else:
                pyvis_net.add_node(0, label = node.name, 
                    color = node.color, title = node.name, 
                    shape = 'circle', margin = 20, value = node.code)
            # choose title
            if node.name in listfl:
                pyvis_net.get_node(key)['title'] += ': Listed' 
            else:
                pyvis_net.get_node(key)['title'] += \
                    ' ({:.1f}% from listed)' \
                    .format(node.red_trade)
            # add to queues
            if level < levels_n:
                nodes_q.append(key)
            if level > 0:
                partners_q.append(key)
        curr_list = next_list
        level += 1
    
    while nodes_q:
        key = nodes_q.pop()
        i = pyvis_net.get_node(key)['value']
        sum_trade = 0
        for _ in range(imp_n):
            p_key = partners_q.pop()
            j = pyvis_net.get_node(p_key)['value']
            tv = 100*(tradeMat.loc[i, j]/
                    tradeMat.loc[i, 0])
            sum_trade += tv
            if flowCode == "X":
                pyvis_net.get_node(p_key)['title'] += \
                    '\n Imports {:.1f}% of {}\'s Supply' \
                        .format(tv, pyvis_net.get_node(key)['label'])
                pyvis_net.add_edge(key, p_key,
                        title = '{:.0f}%' \
                            .format(tv))
            else:
                pyvis_net.get_node(p_key)['title'] += \
                    '\n Supplies {:.1f}% of {}\'s Import' \
                        .format(tv, pyvis_net.get_node(key)['label'] )
                pyvis_net.add_edge(p_key, key, 
                    title = '{:.1f}%' \
                        .format(tv))
        #parent node title
        #if flowCode == "X" and key == 0:
        if flowCode == "X" :
            pyvis_net.get_node(key)['title'] += \
                '\n {:.1f}% exports to following' \
                .format(min(sum_trade, 100))
        #elif flowCode == "M" and key == 0:
        elif flowCode == "M":
            pyvis_net.get_node(key)['title'] += \
                '\n {:.1f}% imports from preceeding' \
                .format(min(sum_trade, 100))
            
    return

def deep_search(reporterCode, flowCode, imp_n, levels_n, tradeMat, comm_name, year):
    ####
    #BLOCK 1
    ####
    # Based on names and codes in 'areas.csv', 
    # make a dict 'areas_nodes' of node objects keyed by code.
    areas = pd.read_csv('data/areas.csv', index_col = 1)
    areas.drop('Unnamed: 0', axis = 1, inplace = True)
    areas.rename(columns={'text_x' : 'text'}, inplace=True)
    areas_nameTocode = {}
    for i in areas.index:
        areas_nameTocode[areas.loc[i]['text']] = i 
        
    areas_nodes = {}    
    for j in tradeMat.index:
        if j == reporterCode:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, 
                                            areas.loc[j]['text'], -1)
        else:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, 
                                            areas.loc[j]['text'])
    
    for j in tradeMat.columns:
        if j not in areas_nodes.keys() and \
           j in areas.index:
            areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'])
    
    ####
    # BLOCK 2: TRADE CALCULATIONS AND BULDING DATAFRAME
    ####
    if flowCode == "X":
        table = pd.DataFrame(columns = ['a', 'b', 'export', 'flag'])
    elif flowCode == "M":
        table = pd.DataFrame(columns = ['a', 'b', 'import', 'flag'])
    else:
        table = pd.DataFrame(columns = ['a', 'b', 'import', 'export',
                                                            'flag'])
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
    index = 1
    while level <= levels_n + 1:
        next_list = []
        for country in curr_list:
            i = country.code
            if i in tradeMat.index:
                trade = []
                red_trade = 0
                tot_trade = tradeMat.loc[i, 0]
                if tot_trade > 0:
                    for j in tradeMat.columns:
                        if j in areas.index and j > 0:
                            j = areas_nodes[j]
                            tv = tradeMat.loc[i, j.code]
                            if tv > 0:
                                j.trade_value = 100*(tv/tot_trade)
                                trade.append(j)
                                if j.name in listfl:
                                    red_trade += tv
                trade.sort(key = lambda x: x.trade_value, reverse=True)
                idx_trade = min(len(trade), imp_n)
                trade = trade[:idx_trade]
                country.red_trade = 100*(red_trade/tot_trade)
                if len(trade) > 0 and tot_trade > 0:
                    for partner in trade:
                        partner.parent = country.name
                        partner.depth = level
                        if level <= levels_n:
                            country.imp_partners.append(partner)
                        # Build Table    
                        flag = partner.name in listfl or country.name in listfl
                        tr = str(round(partner.trade_value, 2))[:4]
                        if flowCode == "X":
                            table.loc[index] = pd.Series(
                                        {'a':country.name, 
                                        'b':partner.name, 
                                        'export':tr,
                                        'flag': flag})
                        if flowCode == "M":
                            table.loc[index] = pd.Series(
                                            {'a':country.name, 
                                            'b':partner.name, 
                                            'import': tr,
                                            'flag': flag})
                        del tr
                        index += 1
                if tot_trade > 0:
                    next_list.extend(country.imp_partners)
            # node color information
            if country.color == 'white':
                if country.name in listfl:
                    country.color = 'rgba(255,0,0,1)'
                else:
                    country.color = 'rgba(200,{},{},1)'.format(
                                        255*(1 - country.red_trade/100),
                                        255*( 1 - country.red_trade/100))
        curr_list = next_list
        level += 1
    if flowCode == "X":
        table.loc['*'] = pd.Series({'a':'As % of total exports of A'})
    elif flowCode == "M":
        table.loc['*'] = pd.Series({'a':'As % of total imports of A'})
    table.loc[' '] = ('COMMODITY:',comm_name,'','')
    table.loc['  '] = ('YEAR',year,'','')
    ####
    #BLOCK 3: MAKE GRAPH AND SAVE AS HTML
    ####
    # Make a pyvis graph and save it as an html
    #pyvis_net = Network(height="400px", width="100%", 
    #                    bgcolor="#222222", font_color="white", 
    #                    directed=True)
    pyvis_net = Network(height="400px", width="100%", 
                        bgcolor="#222222", font_color="black", 
                        directed=True)
    makePyvisGraph(areas_nodes[reporterCode], pyvis_net, flowCode, levels_n, imp_n, tradeMat)
    ####    
    pyvis_net.write_html("images/result.html", local=True)
    return True, table
    
if __name__ == '__main__':
    deep_search(reporterCode, flowCode, imp_n, levels_n, tradeMat, comm_name, year)