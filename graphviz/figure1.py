# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Uses pygraphviz to illustrate the inner structure of NSDF file format
# This is to use in the NSDF paper and to generate machine readable file structure
# for the convenience of the user.

# Use matplotlib and pygraphviz

import matplotlib.pyplot as plt
import pygraphviz as pgv
import webcolors as wc

width_box = 1
edge_width = 2.0

font_name = 'Arial'
font_size = 12.0

subgrp_shape = 'tab' #http://www.graphviz.org/doc/info/shapes.html#d:style
leafnde_shape = 'note'

NODE_0_C = wc.name_to_hex('white') #root
NODE_1_C = wc.name_to_hex('skyblue') #data/map/model
NODE_2_C = wc.name_to_hex('wheat') #uniform/static
NODE_3_C = wc.name_to_hex('lightgreen') #population
NODE_4_C = wc.name_to_hex('sandybrown') #parameter
NODE_5_C = wc.name_to_hex('lightgrey') #oned

def add_children(G, parent_node, child_list, color=None, end_node=False):
    child_node_list = []
    dummy_point_list = []
    children = []
    for child_idx, child in enumerate(child_list):
        child_x = child+'_'+str(G.order()) 
        children.append(child_x)
        if end_node:
            G.add_node(child_x, label=child, width=width_box, shape=leafnde_shape, style='filled', concentrate=True, fillcolor=color, 
                       fontname=font_name, fontsize=font_size)
        else:
            G.add_node(child_x, label=child, width=width_box, shape=subgrp_shape, style='filled', concentrate=True, fillcolor=color, 
                   fontname=font_name, fontsize=font_size)
        G.add_node(child_x+'_point', shape='point', width=0.05)
        child_node = G.get_node(child_x)
        child_point_node = G.get_node(child_x+'_point')
        G.add_edge(child_point_node, child_node, penwidth=edge_width, weight=2)
        child_node_list.append(child_node)
        dummy_point_list.append(child_point_node)

    G.add_edge(parent_node, dummy_point_list[0], arrowhead=None, arrowsize=0.0, penwidth=edge_width)
    for idx in range(len(dummy_point_list)-1):
        G.add_edge(dummy_point_list[idx], dummy_point_list[idx+1], arrowhead=None, arrowsize=0.0, penwidth=edge_width, weight=1)
    H = G.subgraph(child_node_list, rank='same')
    H = G.subgraph(dummy_point_list+[parent_node], rank='same')
    return children

# def unwrap_path(path_list):
#     all_dict = {}
#     for path in path_list:
#         all_eles = path.split('/')[1:]
#         ii=0
#         for ii,jj in enumerate(all_eles):
#             try:
#                 child = all_dict[jj]
#             except KeyError:
#                 all_dict[jj] = {}
#     print all_dict

# test = ['/data/uniform/pop1/Vm',
#         '/data/uniform/pop1/Im',
#         '/data/events/pop1/spikes',
#         '/map/uniform/pop1']

# unwrap_path(test)                
                

def figure1a():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('ROOT', label='ROOT', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_0_C) #root level
    children = add_children(G, 'ROOT', ['model', 'map', 'data'], NODE_1_C) #  #parent level (model/data/map)
    add_children(G, children[2], ['static', 'events', 'uniform', 'nonuniform'], NODE_2_C) #  #Child level (uniform/static)
    G.layout('dot')
    G.draw('figure1a.svg')

def figure1b():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['uniform'], NODE_2_C)
    children = add_children(G, children[0], ['population0', 'population1'], NODE_3_C) #  #Child level (uniform/static)
    add_children(G, children[0], ['Vm', 'Im', 'Gk', 'Ik'], NODE_4_C, True)
    add_children(G, children[1], ['Vm'], NODE_4_C, True)
    G.layout('dot')
    G.draw('figure1b.svg')

def figure1c():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['event'], NODE_2_C) 
    children = add_children(G, children[0], ['population0', 'population1'], NODE_3_C) #  #Child level (uniform/static)
    children_sp1 = add_children(G, children[0], ['spike'], NODE_4_C)
    add_children(G, children_sp1[0], ['spikedataset0','spikedataset1','spikedataset2'], NODE_5_C, True)
    children_sp2 = add_children(G, children[1], ['spike'], NODE_4_C)
    add_children(G, children_sp2[0], ['spikedataset0'], NODE_5_C, True)
    G.layout('dot')
    G.draw('figure1c.svg')

def figure1d():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['nonuniform'], NODE_2_C) 
    children = add_children(G, children[0], ['neurons', 'AMPA', 'GABA'], NODE_3_C) #  #Child level (uniform/static)
    children_sp1 = add_children(G, children[0], ['Im'], NODE_4_C)
    add_children(G, children_sp1[0], ['soma0','soma1'], NODE_5_C, True)
    children_sp2 = add_children(G, children[1], ['Gk'], NODE_4_C)
    add_children(G, children_sp2[0], ['soma_0_ampa', 'dend_0_ampa'], NODE_5_C, True)
    children_sp2 = add_children(G, children[2], ['Gk'], NODE_4_C)
    add_children(G, children_sp2[0], ['dend_0_gaba', 'dend_4_gaba'], NODE_5_C, True)
    G.layout('dot')
    G.draw('figure1d.svg')

figure1a()
figure1b()
figure1c()
figure1d()
