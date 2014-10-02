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
font_size = 12.0 #point size

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

def gen_data_root():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('ROOT', label='ROOT', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_0_C) #root level
    children = add_children(G, 'ROOT', ['model', 'map', 'data'], NODE_1_C) #  #parent level (model/data/map)
    add_children(G, children[2], ['static', 'events', 'uniform', 'nonuniform'], NODE_2_C) #  #Child level (uniform/static)
    G.layout('dot')
    G.draw('data_root.svg')

def gen_data_uniform():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['uniform'], NODE_2_C)
    children = add_children(G, children[0], ['L5Pyr'], NODE_3_C) #  #Child level (uniform/static)
    Vm = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR><TD ROWSPAN="3" BORDER="0" WIDTH="30" HEIGHT="60" FIXEDSIZE="TRUE" ALIGN="CENTER">Vm</TD><TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1,0]</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1,t]</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">cell[P,0]</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">cell[P,t]</TD> </TR></TABLE>>'
    add_children(G, children[0], [Vm], NODE_4_C, True)
    #add_children(G, children[1], [Vm], NODE_4_C, True)
    G.layout('dot')
    G.draw('data_uniform.svg')

def gen_data_event_oned():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['event'], NODE_2_C) 
    children = add_children(G, children[0], ['L5Pyr'], NODE_3_C) #  #Child level (uniform/static)
    children_sp1 = add_children(G, children[0], ['spikes'], NODE_4_C)
    cell1 = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="1" BORDER="0" WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1]</TD><TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[0]</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[11]</TD> </TR> </TABLE>>'
    cellX = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="1" BORDER="0" WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD><TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[0]</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[12]</TD> </TR> </TABLE>>'
    cellP = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="1" BORDER="0" WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[P]</TD><TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[0]</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="40" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[13]</TD> </TR> </TABLE>>'
    add_children(G, children_sp1[0], [cell1,cellX,cellP], NODE_5_C, True)
    G.layout('dot')
    G.draw('data_event_oned.svg')

def gen_data_event_nan():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['events'], NODE_2_C)
    children = add_children(G, children[0], ['L5Pyr'], NODE_3_C)
    spikes = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="3" BORDER="0" WIDTH="50" HEIGHT="60" FIXEDSIZE="TRUE" ALIGN="CENTER">spikes</TD><TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[1,0]</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[1,11]</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">NaN</TD><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">NaN</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">NaN</TD> </TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">sp[P,0]</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">sp[P,13]</TD> </TR></TABLE>>'
    add_children(G, children[0], [spikes], NODE_4_C, True)
    #add_children(G, children[0], ['population1'], NODE_3_C, True)
    G.layout('dot')
    G.draw('data_event_nan.svg')

def gen_data_event_vlen():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['events'], NODE_2_C)
    children = add_children(G, children[0], ['L5Pyr'], NODE_3_C)
    spikes = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="3" BORDER="0" WIDTH="50" HEIGHT="60" FIXEDSIZE="TRUE" ALIGN="CENTER">spikes</TD><TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[1,0]</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">sp[1,11]</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> </TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">sp[P,0]</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">sp[P,13]</TD> </TR></TABLE>>'
    add_children(G, children[0], [spikes], NODE_4_C, True)
    #add_children(G, children[0], ['population1'], NODE_3_C, True)
    G.layout('dot')
    G.draw('data_event_vlen.svg')

def gen_data_nuniform():
    G = pgv.AGraph(strict=True,directed=True, rankdir='LR',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('data', label='data', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C) 
    children = add_children(G, 'data', ['nonuniform'], NODE_2_C) 
    #children = add_children(G, children[0], ['neuronA', 'neuronB'], NODE_3_C) #  #Child level (uniform/static)
    children = add_children(G, children[0], ['cell[1]'], NODE_3_C) #  #Child level (uniform/static)
    Im1 = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="3" BORDER="0" WIDTH="30" HEIGHT="60" FIXEDSIZE="TRUE" ALIGN="CENTER">Im</TD><TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cmpt[1,0]</TD> <TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cmpt[1,M]</TD></TR><TR><TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">...</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">cmpt[N,0]</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">cmpt[N,M]</TD></TR></TABLE>>'
#    Im2 = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD ROWSPAN="2" BORDER="0" WIDTH="30" HEIGHT="60" FIXEDSIZE="TRUE" ALIGN="CENTER">Im</TD><TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">soma[0]</TD> <TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD> <TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">soma[N]</TD> </TR> <TR> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">dend[0]</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">...</TD> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">dend[N]</TD> </TR></TABLE>>'
    children_sp1 = add_children(G, children[0], [Im1], NODE_4_C, True)
    #add_children(G, children[1], [Im2], NODE_4_C, True)
    G.layout('dot')
    G.draw('data_nuniform.svg')

def gen_map_uniform():
    #RHS
    G = pgv.AGraph(strict=True,directed=True, rankdir='RL',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['uniform'], NODE_2_C)
    neuronA = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1]</TD><TD ROWSPAN="2" BORDER="0" WIDTH="50" HEIGHT="10" FIXEDSIZE="TRUE" ALIGN="CENTER">L5Pyr</TD></TR> <TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD></TR><TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">cell[P]</TD></TR></TABLE>>'
    #neuronB = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">soma</TD><TD ROWSPAN="2" BORDER="0" WIDTH="50" HEIGHT="10" FIXEDSIZE="TRUE" VALIGH="MIDDLE" ALIGN="CENTER">neuronB</TD> </TR> <TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">axon</TD></TR></TABLE>>'
    #add_children(G, children[0], [neuronB], NODE_3_C, True)
    add_children(G, children[0], [neuronA], NODE_3_C, True)

    G.layout('dot')
    G.draw('map_uniform.svg')

def gen_map_nureg():
    #RHS
    G = pgv.AGraph(strict=True,directed=True, rankdir='RL',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['nonuniform'], NODE_2_C)
    cell1 = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cmpt[1]</TD><TD ROWSPAN="3" BORDER="0" WIDTH="50" HEIGHT="10" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1]</TD></TR><TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD></TR> <TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">cmpt[N]</TD></TR></TABLE>>'
    add_children(G, children[0], [cell1], NODE_3_C, True)
    G.layout('dot')
    G.draw('map_nuniform.svg')

def gen_map_time():
    #RHS
    G = pgv.AGraph(strict=True,directed=True, rankdir='RL',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['time'], NODE_2_C)
    neuronA = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">t1</TD><TD ROWSPAN="3" BORDER="0" WIDTH="50" HEIGHT="10" FIXEDSIZE="TRUE" ALIGN="CENTER">tpoints</TD></TR> <TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">...</TD></TR> <TR><TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">tM</TD></TR></TABLE>>'
    add_children(G, children[0], [neuronA], NODE_3_C, True)
    G.layout('dot')
    G.draw('map_time.svg')

def gen_map_event_vlen():
    #RHS
    G = pgv.AGraph(strict=True,directed=True, rankdir='RL',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['events'], NODE_2_C)
    cells = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">neuronA</TD><TD ROWSPAN="2" BORDER="0" WIDTH="45" HEIGHT="10" FIXEDSIZE="TRUE" ALIGN="CENTER">cells</TD></TR> <TR> <TD ALIGN="CENTER" WIDTH="50" HEIGHT="30" FIXEDSIZE="TRUE">neuronB</TD></TR></TABLE>>'
    #neuronB = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">soma</TD><TD ROWSPAN="2" BORDER="0" WIDTH="50" HEIGHT="10" FIXEDSIZE="TRUE" VALIGH="MIDDLE" ALIGN="CENTER">neuronB</TD> </TR> <TR> <TD ALIGN="CENTER" WIDTH="45" HEIGHT="30" FIXEDSIZE="TRUE">axon</TD></TR></TABLE>>'
    add_children(G, children[0], [cells], NODE_3_C, True)
    #add_children(G, children[0], [neuronA], NODE_3_C, True)
    G.layout('dot')
    G.draw('map_event_vlen.svg')

def gen_map_event_oned():
    #RHS
    G = pgv.AGraph(strict=True,directed=True, rankdir='RL',ranksep='0.25', splines=False, nodesep=0.25)#, rank='source')
    G.add_node('map', label='map', shape=subgrp_shape, style='filled', concentrate=True, width=width_box,
               fontname=font_name, fontsize=font_size, fillcolor=NODE_1_C)
    children = add_children(G, 'map', ['events'], NODE_2_C)
    children = add_children(G, children[0], ['L5Pyr'], NODE_3_C)
    spike = '<<TABLE ALIGN="CENTER" BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="2" FIXEDSIZE="TRUE"> <TR> <TD COLSPAN="2" BORDER="0" WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">spikes</TD></TR> <TR><TD WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER" >source</TD><TD WIDTH="180" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">data</TD></TR> <TR><TD WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[1]</TD><TD WIDTH="180" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">/data/events/L5Pyr/spike/cell[1]</TD></TR><TR><TD WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">...</TD><TD WIDTH="180" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">/data/events/L5Pyr/spike/...</TD></TR><TR><TD WIDTH="55" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">cell[P]</TD><TD WIDTH="180" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER">/data/events/L5Pyr/spike/cell[P]</TD></TR> </TABLE>>'
    add_children(G, children[0], [spike], NODE_4_C, True)
    #add_children(G, children[0], ['population1'], NODE_3_C, True)
    G.layout('dot')
    G.draw('map_event_oned.svg')

gen_data_uniform()
gen_data_event_nan()
gen_data_event_vlen()
gen_data_event_oned()
gen_data_nuniform()

gen_map_uniform()
gen_map_event_oned()
gen_map_event_vlen()
gen_map_nureg()
gen_map_time()
