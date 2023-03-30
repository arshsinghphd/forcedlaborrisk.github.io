import countryNode  
import numpy as np
import pandas as pd
from pyvis.network import Network
import requests 
import streamlit as st

listfl = list(pd.read_csv('data/listfl_cotton.csv')['0'])

def makePyvisGraph(node, pyvis_net, flowCode, imp_n):
    if node.name not in pyvis_net.get_nodes():
        if node.name in listfl:
            pyvis_net.add_node(node.name,
                            title = node.name + ': Listed' +\
                            '\n {:.1f}% imports from listed'
                                .format(node.red_trade), 
                            color = node.color,
                            shape = 'circle',
                            margin = 20
                          )
        else:
            pyvis_net.add_node(node.name,
                            title = node.name +\
                            '\n {:.1f}% imports from listed'
                                .format(node.red_trade), 
                            color = node.color,
                            shape = 'circle',
                            margin = 20
                          )
    sum_trade = 0
    if node.imp_partners:
        for partner in node.imp_partners:
            sum_trade += partner.trade_value
            if flowCode == "X":
                if partner.name in listfl:
                    pyvis_net.add_node(partner.name,
                                title = partner.name + ': Listed' \
                                + '\n Imports {:.1f}% of {}\'s Supply'
                                .format(partner.trade_value, 
                                        partner.parent),
                                color = partner.color,
                                shape = 'box')
                else:
                    pyvis_net.add_node(partner.name,
                                title = partner.name + \
                                '\n {:.1f}% imports from listed countries'
                                .format(partner.red_trade)
                                + '\n Imports {:.1f}% of {}\'s Supply'
                                .format(partner.trade_value, 
                                        partner.parent),
                                color = partner.color,
                                shape = 'box')
                pyvis_net.add_edge(node.name, partner.name,
                        title = '{:.0f}%'.format(partner.trade_value))
                makePyvisGraph(partner, pyvis_net, flowCode, imp_n)
            elif flowCode == "M":
                if partner.name in listfl:
                    pyvis_net.add_node(partner.name,
                                title = partner.name + ': Listed' + 
                                '\n Supplies {:.1f}% of {}\'s Import'
                                .format(partner.trade_value, 
                                        partner.parent),
                                color = partner.color,
                                shape = 'box')
                else:
                    pyvis_net.add_node(partner.name,
                                title = partner.name + \
                                '\n {:.1f}% imports from listed countries'
                                .format(partner.red_trade) + 
                                '\n Supplies {:.1f}% of {}\'s Import'
                                .format(partner.trade_value, 
                                        partner.parent),
                                color = partner.color,
                                shape = 'box')
                pyvis_net.add_edge(partner.name, node.name, 
                        title = '{:.1f}%'.format(partner.trade_value))
                makePyvisGraph(partner, pyvis_net, flowCode, imp_n)
        if flowCode == "X":
            if node.parent == 0:
                pyvis_net.get_node(node.name)['title'] += \
                '\n {:.1f}% exports to following'\
                                            .format(min(sum_trade, 100), imp_n)
        elif flowCode == "M":
            if node.parent == 0:
                pyvis_net.get_node(node.name)['title'] += \
                '\n {:.1f}% imports from preceeding'\
                                            .format(min(sum_trade, 100), imp_n)
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
            if country.code == reporterCode:
                country.engaged = True
            i = country.code
            if i in tradeMat.index:
                trade = []
                red_trade = 0
                for j in tradeMat.columns:
                    if j in areas.index:
                        j = areas_nodes[j]
                        tv = 0
                        if not j.engaged and j.code > 0:
                            tv = tradeMat.loc[i, j.code]
                            if tv > 0:
                                j.trade_value = tv
                        trade.append(j)
                        if j.name in listfl:
                            red_trade += tradeMat.loc[i, j.code]
                        del tv
                trade.sort(key = lambda x: x.trade_value, reverse=True)
                idx_trade = min(len(trade), imp_n)
                trade = trade[:idx_trade]
                tot_trade = tradeMat.loc[i, 0]
                red_trade = (red_trade/tot_trade)*100
                country.red_trade = red_trade
                counter = 0
                if len(trade) > 0 and tot_trade > 0:
                    for partner in trade:
                        counter += 1
                        if not partner.engaged:
                            partner.trade_value = \
                                    100*(partner.trade_value/tot_trade)
                            partner.parent = country.name
                            partner.color = country.color
                            partner.engaged = True
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
    makePyvisGraph(areas_nodes[reporterCode], pyvis_net, flowCode, imp_n)
    ####    
    pyvis_net.write_html("images/result.html", local=True)
    return True, table


if __name__ == '__main__':
    deep_search(reporterCode, flowCode, imp_n, levels_n, tradeMat, comm_name, year)