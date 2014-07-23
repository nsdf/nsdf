# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Uses pygraphviz to illustrate the inner structure of NSDF file format
# This is to use in the NSDF paper and to generate machine readable file structure
# for the convenience of the user.

# Use matplotlib and pygraphviz

import matplotlib.pyplot as plt
import pygraphviz as pgv

G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.5', splines=False, nodesep=0.5)#, rank='source')

width_box = 2

def add_children(G, parent_node, child_list, color=None):
    child_node_list = []
    dummy_point_list = []
    children = []
    for child_idx, child in enumerate(child_list):
        try:
            doh_ = G.get_node(child)
            child_x = child+'_'+str(G.order())
        except KeyError:
            child_x = child
        children.append(child_x)
        G.add_node(child_x, label=child, width=width_box, shape='box', style='rounded,filled', concentrate=True, fillcolor=color)
        G.add_node(child_x+'_point', shape='point')

        child_node = G.get_node(child_x)
        child_point_node = G.get_node(child_x+'_point')

        G.add_edge(child_point_node, child_node, weight=2)

        child_node_list.append(child_node)
        dummy_point_list.append(child_point_node)

    G.add_edge(parent_node, dummy_point_list[0], arrowhead=None, arrowsize=0.0)
    for idx in range(len(dummy_point_list)-1):
        G.add_edge(dummy_point_list[idx], dummy_point_list[idx+1], arrowhead=None, arrowsize=0.0, weight=1)

    H = G.subgraph(child_node_list, rank='same')
    H = G.subgraph(dummy_point_list+[parent_node], rank='same')

    return G, children

#  #BASIC ROOT level in HDF5
G.add_node('ROOT', label='ROOT', shape='box', style='rounded,filled', concentrate=True) #root level
add_children(G, 'ROOT', ['model', 'map', 'data'], 'red') #  #parent level (model verus map)
add_children(G, 'data', ['static', 'events', 'uniform', 'nonuniform'], 'green') #  #Child level (data type)

add_children(G, 'static', ['all'], 'orange') #  #Grandchild (population)
add_children(G, 'all', ['morphology'], 'blue') #  #Great-grandchild
add_children(G, 'all', ['connections'], 'blue')

add_children(G, 'events', ['population0', 'population1'], 'orange')
G, children = add_children(G, 'population0', ['spikes'], 'blue')
add_children(G, children[0], ['spikedataset0', 'spikedataset1', 'spikedataset2'])
G, children = add_children(G, 'population1', ['spikes'], 'blue')
add_children(G, children[0], ['spikedataset0', 'spikedataset1', 'spikedataset2'])

G, children = add_children(G, 'uniform', ['population0', 'population1'], 'orange')
add_children(G, children[0], ['Vm','Im', 'Ik'], 'blue')
add_children(G, children[1], ['Vm'], 'blue')

add_children(G, 'nonuniform', ['neurons', 'AMPA', 'GABA'], 'orange')
G, children = add_children(G, 'neurons', ['Vm'], 'blue')
add_children(G, children[0], ['soma_0', 'soma_1'])
add_children(G, 'AMPA', ['Gk'], 'blue')
add_children(G, 'Gk', ['soma_0_ampa'])
add_children(G, 'Gk', ['dend_1_ampa'])
G, children = add_children(G, 'GABA', ['Gk'], 'blue')
add_children(G, children[0], ['soma_0_gaba'])
add_children(G, children[0], ['dend_4_gaba'])
add_children(G, children[0], ['dend_7_gaba'])

G.layout('dot')
G.draw('figure1.png')
# End of figure1.py
