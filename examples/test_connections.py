from builtins import str
from builtins import range
# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Illustrates how to store connectivity information. 
# file format using h5py. Optional storage from BRIAN Simulator

# Use h5py >= 2.3

import h5py
import numpy as np

USE_BRIAN = False

if USE_BRIAN: 
    from brian import *
    eqs = '''
    dv/dt = (ge+gi-(v+49*mV))/(20*ms) : volt
    dge/dt = -ge/(5*ms) : volt
    dgi/dt = -gi/(10*ms) : volt
    '''
    num_neurons = 2 #in 1e03
    sim_time = 2 #in seconds
    P = NeuronGroup(1000*num_neurons, eqs, threshold=-50*mV, reset=-60*mV)
    P.v = -60*mV+10*mV*rand(len(P))
    Pe = P.subgroup(800*num_neurons)
    Pi = P.subgroup(200*num_neurons)
    Ce = Connection(Pe, P, 'ge', weight=1.62*mV, sparseness=0.02)
    Ci = Connection(Pi, P, 'gi', weight=-9*mV, sparseness=0.02)
    ex_pre = []
    ex_post = []
    ex_wts = []
    for pre in range(len(Pe)):
        for post in range(len(P)): 
            qq = Ce[pre, post]
            if qq != 0.0:
                ex_pre.append(pre)
                ex_post.append(post)
                ex_wts.append(qq)
    in_pre = []
    in_post = []
    in_wts = []
    for pre in range(len(Pi)):
        for post in range(len(P)): 
            qq = Ci[pre, post]
            if  qq != 0.0:
                in_pre.append(pre)
                in_post.append(post)
                in_wts.append(qq)
else:
    ex_pre = np.random.randint(1000, size=(500,))
    ex_post = np.random.randint(1000, size=(500,))
    ex_wts = np.random.rand(1000)
    in_pre = np.random.randint(1000, size=(500,))
    in_post = np.random.randint(1000, size=(500,))
    in_wts = np.random.rand(1000)

def tie_data_map(d_set, m_set, name, axis=0):
    d_set.dims[axis].label = name
    m_set.make_scale(name)
    d_set.dims[axis].attach_scale(m_set)
    m_set.attrs.create('NAME', data='source')

def connection_1():
    h = h5py.File('Brian_conn_1.h5', 'w')
    sp_type = np.dtype([('pre', h5py.special_dtype(vlen=str)), ('post', h5py.special_dtype(vlen=str)), ('weight', np.float64)])
    #excitatory
    syn_ids = h.create_dataset('/map/static/ex_synapses', data=list(range(len(ex_pre))), dtype=np.int)
    exc_ds = h.create_dataset('/data/static/syapses/exc', dtype=sp_type, shape=(len(ex_pre),) )
    for ii in range(len(ex_pre)):
        exc_ds[ii] = (str(ex_pre[ii]), str(ex_post[ii]), ex_wts[ii])
    tie_data_map(exc_ds, syn_ids, 'syn_ids', axis=0)
    exc_ds.attrs.create('unit', data=['null', 'null', 'mV'])
    #inhibitory
    syn_ids = h.create_dataset('/map/static/in_synapses', data=list(range(len(in_pre))), dtype=np.int)
    inh_ds = h.create_dataset('/data/static/syapses/inh', dtype=sp_type, shape=(len(in_pre),) )
    for ii in range(len(in_pre)):
        inh_ds[ii] = (str(in_pre[ii]), str(in_post[ii]), in_wts[ii])
    tie_data_map(inh_ds, syn_ids, 'syn_ids', axis=0)
    inh_ds.attrs.create('unit', data=['null', 'null', 'mV'])
    h.close()

def connection_2():
    h = h5py.File('Brian_conn_2.h5', 'w')
    #excitatory
    syn_ids = h.create_dataset('/map/static/ex_synapses', data=list(range(len(ex_pre))), dtype=np.int)
    exc_pre_ds = h.create_dataset('/data/static/exc_syapses/pre', data=ex_pre, dtype=np.int)
    exc_post_ds = h.create_dataset('/data/static/exc_syapses/post', data=ex_post, dtype=np.int)
    exc_wts = h.create_dataset('/data/static/exc_syapses/wts', data=ex_wts, dtype=np.float64)
    tie_data_map(exc_pre_ds, syn_ids, 'pre', axis=0)
    tie_data_map(exc_post_ds, syn_ids, 'post', axis=0)
    tie_data_map(exc_wts, syn_ids, 'weights', axis=0)
    exc_pre_ds.attrs.create('field', data='pre')
    exc_pre_ds.attrs.create('unit', data='null')
    exc_post_ds.attrs.create('field', data='post')
    exc_post_ds.attrs.create('unit', data='null')
    exc_wts.attrs.create('field', data='weight')
    exc_wts.attrs.create('unit', data='mV')
    #inhibitory
    syn_ids = h.create_dataset('/map/static/in_synapses', data=list(range(len(in_pre))), dtype=np.int)
    inh_pre_ds = h.create_dataset('/data/static/inh_syapses/pre', data=in_pre, dtype=np.int)
    inh_post_ds = h.create_dataset('/data/static/inh_syapses/post', data=in_post, dtype=np.int)
    inh_wts = h.create_dataset('/data/static/inh_syapses/wts', data=in_wts, dtype=np.float64)
    tie_data_map(inh_pre_ds, syn_ids, 'pre', axis=0)
    tie_data_map(inh_post_ds, syn_ids, 'post', axis=0)
    tie_data_map(inh_wts, syn_ids, 'weights', axis=0)
    inh_pre_ds.attrs.create('field', data='pre')
    inh_pre_ds.attrs.create('unit', data='null')
    inh_post_ds.attrs.create('field', data='post')
    inh_post_ds.attrs.create('unit', data='null')
    inh_wts.attrs.create('field', data='weight')
    inh_wts.attrs.create('unit', data='mV')

def connection_3(): #DO NOT RECOMMEND! Ineffective means of storing information
    exc_mat = Ce.W.todense()
    inh_mat = Ci.W.todense()
    h = h5py.File('Brian_conn_3.h5', 'a')
    exc_ds = h.create_dataset('/data/static/synapses/exc', data=exc_mat, dtype=np.float64)
    exc_ds.attrs.create('field', data='weight')
    exc_ds.attrs.create('unit', data='mV')
    exc_pre = h.create_dataset('/map/static/exc_pre', data=list(range(exc_mat.shape[0])), dtype=np.int)
    exc_post = h.create_dataset('/map/static/post', data=list(range(exc_mat.shape[1])), dtype=np.int)
    tie_data_map(exc_ds, exc_pre, 'pre', axis=0)
    tie_data_map(exc_ds, exc_post, 'post', axis=1)
    inh_ds = h.create_dataset('/data/static/synapses/inh', data=inh_mat, dtype=np.float64)
    inh_ds.attrs.create('field', data='weight')
    inh_ds.attrs.create('unit', data='mV')
    inh_pre = h.create_dataset('/map/static/inh_pre', data=list(range(inh_mat.shape[0])), dtype=np.int)
    tie_data_map(inh_ds, inh_pre, 'pre', axis=0)
    tie_data_map(inh_ds, exc_post, 'post', axis=1)
    h.close()

connection_1()
connection_2()
#connection_3()

#End of file
