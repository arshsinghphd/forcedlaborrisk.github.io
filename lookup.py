import countryNode  

import numpy as np
import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

listfl = list(pd.read_csv('data/listfl_cotton.csv')['0'])

def makePyvisGraph(node, pyvis_net, flowCode, ncolor = 'white'):
    # Node color
    if node.name in listfl:
        ncolor = 'red'    
    if node.name not in pyvis_net.get_nodes():
        pyvis_net.add_node(node.name, 
                            title = node.name, 
                            color = ncolor, 
                            size = 12)
    else:
        pyvis_net.get_node(node.name)['color'] = ncolor
    sum_trade = 0
    if node.imp_partners:
        for partner in node.imp_partners:
            sum_trade += partner.trade_value
            if flowCode == "X":
                pyvis_net.add_node(partner.name, 
                                title = '{} \n Imports {:.2f}% of {}\'s Supply'
                                .format(partner.name, 
                                        partner.trade_value, 
                                        partner.parent), 
                                color = ncolor,
                                size = 12 - 2*partner.depth)
                pyvis_net.add_edge(node.name, partner.name,
                        title = '{:.2f}%'.format(partner.trade_value))
                if ncolor == "white":
                    makePyvisGraph(partner, pyvis_net, flowCode)
                else:
                    makePyvisGraph(partner, pyvis_net, flowCode, ncolor)
            elif flowCode == "M":
                if partner.name in listfl:
                    ncolor = 'red'
                pyvis_net.add_node(partner.name, 
                        title = '{} \n Supplies {:.2f}% of {}\'s Import'
                        .format(partner.name, 
                                partner.trade_value, 
                                partner.parent),
                        color = ncolor,
                        size = 12 - 2*partner.depth)
                pyvis_net.add_edge(partner.name, node.name, 
                        title = '{:.2f}%'.format(partner.trade_value))
                makePyvisGraph(partner, pyvis_net, flowCode)
        if flowCode == "X":
            pyvis_net.get_node(node.name)['title'] += \
                '\n {:.2f}% of its exports go to following'.format(sum_trade)
        elif flowCode == "M":
            pyvis_net.get_node(node.name)['title'] += \
                '\n {:.2f}% of its imports come from the preceeding'.format(sum_trade)
    return 

@st.cache_data
def make_mat(year, comm_codes, flowCode):
    df = pd.read_csv('data/{}_{}_{}.csv'.format(flowCode, comm_codes, year), encoding = 'cp437')
    df = df[['ReporterCode','PartnerCode','PrimaryValue']]
    ids = list(df['ReporterCode'] + df['PartnerCode']).unique()
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
    return tradeMat, ids
    
def deep_search(reporterCode, year, comm_codes, flowCode, imp_n, levels_n):
    ####
    #BLOCK 1 
    ####
    # Based on the dat from UN Comtrade, make tradeMat
    # If there is not data for reporterCode in the tradeMat, return None already
    
    # tradeMat = pd.read_csv('data/tradeMat.csv')
    # tradeMat.set_index('id', inplace = True)
    # tradeMat.head()
    
    tradeMat, ids = make_mat(year, comm_codes, flowCode)

    if reporterCode not in ids:
        return False, 0
    
    ####
    #BLOCK 2 
    ####
    # Based on names and codes in 'areas.csv', 
    # make a dict 'areas_nodes' of node objects keyed by code.
    
    areas = pd.read_csv('data/areas.csv', )
    areas.rename(columns={'text_x' : 'text'}, inplace=True)
    areas.set_index('id', inplace = True)
    # make a dict of names to codes
    areas_nameTocode = {}
    for i in areas.index:
        areas_nameTocode[areas.loc[i]['text']] = i 
    areas_nodes = {}
        
    for j in tradeMat.index:
        if j == reporterCode:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'], 0)
        else:
            if j not in areas_nodes.keys():
                areas_nodes[j] = countryNode.node(j, areas.loc[j]['text'])
    
    
    ####
    # BLOCK 3: TRADE CALCULATIONS AND BULDING DATAFRAME
    ####
    if flowCode == "X":
        table = pd.DataFrame(columns = ['a', 'b', 'export', 'flag'])
    elif flowCode == "M":
        table = pd.DataFrame(columns = ['a', 'b', 'import', 'flag'])
    else:
        table = pd.DataFrame(columns = ['a', 'b', 'import', 'export', 'flag'])
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
                    #tv = tradeMat.loc[i, str(j.code)]
                    tv = tradeMat.loc[i, j.code]
                    if tv > 0:
                        j.trade_value = tv
                        trade.append(j)
                        tot_trade += tv
            trade.sort(key = lambda x: x.trade_value, reverse=True)
            idx_trade = min(len(trade), imp_n)
            trade = trade[:idx_trade]
            sum_trade = 0
            counter = 0
            if len(trade) > 0:
                for partner in trade:
                    counter += 1
                    if not partner.engaged:
                        sum_trade += partner.trade_value
                        partner.trade_value = 100*(partner.trade_value/tot_trade)
                        country.imp_partners.append(partner)
                        partner.parent = country.name
                        partner.color = country.color
                        partner.engaged = True
                        partner.depth = level
                        if flowCode == "X":
                            flag = partner.color == 'red'                            
                            exp = str(round(partner.trade_value, 2))[:4]
                            table.loc[index] = pd.Series({'a':country.name, 
                                                  'b':partner.name, 
                                                  'export':exp,
                                                      'flag': flag})
                        if flowCode == "M":
                            imp = str(round(partner.trade_value, 2))[:4]
                            table.loc[index] = pd.Series({'a':country.name, 
                                                      'b':partner.name, 
                                                      'import':imp,
                                                      'flag':False})
                        index += 1
            if tot_trade > 0:
                country.trade_with_partners = (sum_trade/tot_trade)*100
                next_list.extend(country.imp_partners)
        curr_list = next_list
        level += 1
    if flowCode == "X":
        table.loc['*'] = pd.Series({'a':'As % of total exports of A'})
    elif flowCode == "M":
        table.loc['*'] = pd.Series({'a':'As % of total imports of A'})
    
    
    ####
    #BLOCK 4: MAKE GRAPH AND SAVE AS HTML
    ####
    # Make a pyvis graph and save it as an html
    pyvis_net = Network(height="400px", width="100%", 
                        bgcolor="#222222", font_color="white", 
                        directed=True)
    makePyvisGraph(areas_nodes[reporterCode], pyvis_net, flowCode)
    if flowCode == 'M':
        for node in pyvis_net.get_nodes():
            if pyvis_net.get_node(node)['color'] == 'red':
                table.loc[table['b'] == node, 'flag'] = True
                node_code = areas_nameTocode[node]
                parent = areas_nodes[node_code].parent
                while parent != 0:
                    pyvis_net.get_node(parent)['color'] = 'red'
                    table.loc[table['b'] == parent, 'flag'] = True
                    node = parent
                    node_code = areas_nameTocode[node]
                    parent = areas_nodes[node_code].parent
    ####    
    pyvis_net.write_html("images/result.html", local=True)
    
    return True, table
    
    
if __name__ == '__main__':
    deep_search(reporterCode,year,comm_codes,flowCode,imp_n,levels_n)
