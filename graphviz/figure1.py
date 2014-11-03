# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Uses pygraphviz to illustrate the inner structure of NSDF file format
# This is to use in the NSDF paper and to generate machine readable file structure
# for the convenience of the user.

# Use matplotlib and pygraphviz
import re
import matplotlib.pyplot as plt
import pygraphviz as pgv
import webcolors as wc

width_box = 1.0
edge_width = 2.0

font_name = 'Arial'
font_size = 12.0

subgrp_shape = 'tab' #http://www.graphviz.org/doc/info/shapes.html#d:style
leafnde_shape = 'note'

NODE_0 = wc.name_to_hex('white') #root
NODE_1 = wc.name_to_hex('skyblue') #data/map/model
NODE_2 = wc.name_to_hex('wheat') #uniform/static
NODE_3 = wc.name_to_hex('lightgreen') #population
NODE_4 = wc.name_to_hex('sandybrown') #parameter
NODE_5 = wc.name_to_hex('lightgrey') #oned

NODE_COLOR = [NODE_0, NODE_1, NODE_2, NODE_3, NODE_4, NODE_5]

def add_child(G, parent_node, child, color=None, end_node=False):
    if parent_node=='/':
        child_x = parent_node+child 
    else:
        child_x = parent_node+'/'+child 
    G.add_node(child_x+'_point', shape='point', width=0.05)
    child_point_node = G.get_node(child_x+'_point')
    G.add_edge(parent_node, child_point_node, weight=2, penwidth=edge_width, arrowsize=0.0, arrowhead=None, constraint=False)
    if end_node:
        G.add_node(child_x, label=child, width=width_box, shape=leafnde_shape, style='filled', concentrate=True, fillcolor=color, 
                   fontname=font_name, fontsize=font_size)
    else:
        G.add_node(child_x, label=child, width=width_box, shape=subgrp_shape, style='filled', concentrate=True, fillcolor=color, 
                   fontname=font_name, fontsize=font_size)
    child_node = G.get_node(child_x)
    G.add_edge(child_point_node, child_node, penwidth=edge_width, weight=3)
    H = G.subgraph([child_point_node, parent_node], rank='same', constraint=False)
    H = G.subgraph([child_point_node, child], rank='same')
    return child_node

def gen_figure(dir_list):
    G = pgv.AGraph(strict=True, directed=True, rankdir='LR', ranksep='0.25', splines=False, nodesep=0.25)
    G.add_node('/', label='ROOT', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_0)
    for path in dir_list:
        if path.startswith('/'):
            pass
        else:
            path = '/'+path #starting with root
        path_idx = [m.start() for m in re.finditer('/', path)]
        sub_dirs = path.split('/')[1:] #skip the first
        for ii,sub_folder in enumerate(sub_dirs):
            try: 
                dummy = G.get_node(path[:path_idx[ii]]+'/'+sub_folder)
                #print 'Node already exists:', path[:path_idx[ii]]+'/'+sub_folder
                pass
            except KeyError:
                if ii==0:
                    add_child(G, '/', sub_folder, NODE_COLOR[ii+1])
                else:
                    add_child(G, path[:path_idx[ii]], sub_folder, NODE_COLOR[ii+1])
    G.layout('dot')
    G.draw('figure2_lhs.svg')

dir_list = ['/event/kill/me',
            '/data/list/tada/hello',
            'event/tell/this',
            '/data/list/tada/meow']

gen_figure(dir_list)
