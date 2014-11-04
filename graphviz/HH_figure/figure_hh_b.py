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
edge_width = 1.0

font_name = 'Arial'
font_size = 12.0 #in pts

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
    G = pgv.AGraph(strict=True, directed=True, rankdir='LR', ranksep='0.15', splines=False, nodesep=0.25)
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
                elif ii==3 :
                    add_child(G, path[:path_idx[ii]], sub_folder, NODE_COLOR[ii+1], True)
                elif ii==2 and path.find('map')!=-1:
                    add_child(G, path[:path_idx[ii]], sub_folder, NODE_COLOR[ii+1], True)
                else:
                    add_child(G, path[:path_idx[ii]], sub_folder, NODE_COLOR[ii+1])

    return G

def add_leaf(G, parent, leaf_name, leaf_html):
    G.add_node(leaf_name, label=leaf_html, shape='box', style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_4)
    G.add_edge(parent, leaf_name, weight=1, penwidth=edge_width, arrowsize=0.0, style='dashed', 
               arrowhead=None, constraint=True, headport="nw", tailport="ne")
    G.add_edge(leaf_name, parent, weight=1, penwidth=edge_width, arrowsize=0.0, style='dashed', 
               arrowhead=None, constraint=True, headport="se", tailport="sw")
    #leaf_point_node = G.get_node(parent+'_point')
    #H = G.subgraph([leaf_name, parent], rank='max', constraint=False)
    return G


# dir_list = ['/data/event',
#             '/data/nonuniform',
#             '/data/static',
#             '/data/uniform/channel/Ik',
#             '/data/uniform/compartment/Vm',
#             '/map/event',
#             '/map/nonuniform',
#             '/map/static',
#             '/map/time',
#             '/map/uniform/channel',
#             '/map/uniform/compartment',
#             '/model/modeltree/compartment/KChannel',
#             '/model/modeltree/compartment/NaChannel']

dir_list = ['/data/uniform/channel/IChannel',
            '/data/uniform/compartment/Im',
            '/data/uniform/compartment/Vm',
            '/map/uniform/channel',
            '/map/uniform/compartment',
            '/model/modeltree/compartment/KChannel',
            '/model/modeltree/compartment/NaChannel']

G = gen_figure(dir_list)
# add_leaf(G, dir_list[0], 'static', static)
# add_leaf(G, dir_list[1], 'vm', Vm)
# add_leaf(G, dir_list[3], 'im', Im1)
# add_leaf(G, dir_list[4], 'spikes', spikes)

G.layout('dot')
G.draw('figure_hh_b.svg')
