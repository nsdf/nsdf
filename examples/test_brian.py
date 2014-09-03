# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Uses brain simulator's default program to dump the data into NSDF file format
# using h5py. This was used to benchmark performance of different flavours of 
# storing the spike time information.

# Use h5py >= 2.3

import h5py
import numpy as np
from brian import *
import sys
sys.path.append('../..')
import nsdf

seed_no = 500
np.random.seed(seed_no)
#seed(seed_no)
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

Me = SpikeMonitor(Pe)
Mi = SpikeMonitor(Pi)
run(sim_time*second)

def tie_data_map(d_set, m_set, name, axis=0):
    d_set.dims[axis].label = name
    d_set.dims.create_scale(m_set, name)
    d_set.dims[axis].attach_scale(m_set)
    m_set.attrs.create('NAME', data='SOURCE')
e_spikes = len(Me.spiketimes)
i_spikes = len(Mi.spiketimes)

### vlen arrays
def h5_vlen():
    h = h5py.File('Brian_vlen_'+str(seed_no)+'.h5', 'a')
    e_dset = h.create_dataset('/data/events/excitatory/spikes', dtype=h5py.special_dtype(vlen='float32'), shape=(e_spikes,))
    i_dset = h.create_dataset('/data/events/inhibitory/spikes', dtype=h5py.special_dtype(vlen='float32'), shape=(i_spikes,))
    e_list = []
    i_list = []
    for ii in range(e_spikes):
        e_dset[ii] = Me[ii]
        e_list.append('nrn_'+str(ii))
    for ii in range(i_spikes):
        i_dset[ii] = Mi[ii]
        i_list.append('nrn_'+str(ii))
    e_ref = h.create_dataset('/map/events/excitatory/spikes_name', data=e_list)
    i_ref = h.create_dataset('/map/events/inhibitory/spikes_name', data=i_list)
    tie_data_map(e_dset, e_ref, 'SOURCE', 0)
    tie_data_map(i_dset, i_ref, 'SOURCE', 0)
    h.close()

### NaN filled arrays
def h5_nan():
    h = h5py.File('Brian_NaN_'+str(seed_no)+'.h5', 'a')
    e_max = 0
    i_max = 0
    for ii in range(e_spikes):
        e_max = max(e_max, len(Me[ii]))
    for ii in range(i_spikes):
        i_max = max(i_max, len(Mi[ii]))
    e_dset = h.create_dataset('/data/events/excitatory/output', dtype=np.float32, shape=(e_spikes, e_max))
    i_dset = h.create_dataset('/data/events/inhibitory/output', dtype=np.float32, shape=(i_spikes, i_max))
    e_list = []
    i_list = []
    for ii in range(e_spikes):
        e_dset[ii] = np.hstack((Me[ii], [np.NaN]*(e_max-len(Me[ii]))))
        e_list.append('nrn_'+str(ii))
    for ii in range(i_spikes):
        i_dset[ii] = np.hstack((Mi[ii], [np.NaN]*(i_max-len(Mi[ii]))))
        i_list.append('nrn_'+str(ii))
    e_ref = h.create_dataset('/map/events/excitatory/output_name', data=e_list)
    i_ref = h.create_dataset('/map/events/inhibitory/output_name', data=i_list)
    tie_data_map(e_dset, e_ref, 'SOURCE', 0)
    tie_data_map(i_dset, i_ref, 'SOURCE', 0)
    h.close()

### Compound arrays
def h5_cmpd():
    h = h5py.File('Brain_compound_'+str(seed_no)+'.h5', 'a')
    maping_ex = {}
    maping_in = {}
    for ii in range(len(Me.spiketimes)):
        if len(Me[ii]) != 0:
            dset = h.create_dataset('/data/events/excitatory/spikes/' + str(ii), data=Me[ii])
            dset.attrs.create('SOURCE', data='nrn_'+str(ii))
            maping_ex['nrn_'+str(ii)] = '/data/events/excitatory/spikes/' + str(ii)
    for ii in range(len(Mi.spiketimes)):
        if len(Mi[ii]) != 0:
            dset = h.create_dataset('/data/events/inhibitory/spikes/' + str(ii), data=Mi[ii])
            dset.attrs.create('SOURCE', data='nrn_'+str(ii))
            maping_in['nrn_'+str(ii)] = '/data/events/inhibitory/spikes/' + str(ii)
    sp_type = np.dtype([('name', h5py.special_dtype(vlen=str)),('reference', h5py.special_dtype(vlen=str))])
    m_ex = h.create_dataset('/map/events/excitatory/spikes', dtype=sp_type, shape=(len(maping_ex),))
    m_in = h.create_dataset('/map/events/inhibitory/spikes', dtype=sp_type, shape=(len(maping_in),))
    doh_ = 0
    for ii,jj in maping_ex.iteritems():
        m_ex[doh_] = (ii, jj)
        doh_ += 1
    doh_ = 0
    for ii,jj in maping_in.iteritems():
        m_in[doh_] = (ii, jj)
        doh_ += 1
    h.close()

### vlen arrays - using NSDF library
def h5_vlen_nsdf():
    writer = nsdf.NSDFWriter('brian_VLEN_nsdf_'+str(seed_no)+'.h5', mode='w', dialect=nsdf.dialect.VLEN)
    e_list = []
    
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    for ii in range(e_spikes):
        uid = 'nrn_'+str(ii)
        dataobj.put_data(uid, Me[ii])
        e_list.append(uid)
    source_ds = writer.add_event_ds('excitatory', e_list)
    writer.add_event_vlen(source_ds, dataobj)

    i_list = []
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    for ii in range(i_spikes):
        uid = 'nrn_'+str(ii)
        dataobj.put_data(uid, Mi[ii])
        i_list.append(uid)
    source_ds = writer.add_event_ds('inhibitory', i_list)
    writer.add_event_vlen(source_ds, dataobj)


### NaN filled arrays - using NSDF library
def h5_nan_nsdf():
    writer = nsdf.NSDFWriter('brian_NANPADDED_nsdf'+str(seed_no)+'.h5', mode='w', dialect=nsdf.dialect.NANPADDED)
    e_list = []
    
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    for ii in range(e_spikes):
        uid = 'nrn_'+str(ii)
        dataobj.put_data(uid, Me[ii])
        e_list.append(uid)
    source_ds = writer.add_event_ds('excitatory', e_list)
    writer.add_event_nan(source_ds, dataobj)

    i_list = []
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    for ii in range(i_spikes):
        uid = 'nrn_'+str(ii)
        dataobj.put_data(uid, Mi[ii])
        i_list.append(uid)
    source_ds = writer.add_event_ds('inhibitory', i_list)
    writer.add_event_nan(source_ds, dataobj)

### Compound arrays - using NSDF library
def h5_cmpd_nsdf():
    writer = nsdf.NSDFWriter('brian_ONED_nsdf'+str(seed_no)+'.h5', mode='w', dialect=nsdf.dialect.ONED)
    e_list = []
    
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    source_name_dict = {}
    for ii in range(e_spikes):
        uid = 'nrn_'+str(ii)
        source_name_dict[uid] = uid
        dataobj.put_data(uid, Me[ii])
        e_list.append(uid)
    source_ds = writer.add_event_ds_1d('excitatory', 'spikes', e_list)
    writer.add_event_1d(source_ds, dataobj, source_name_dict)

    i_list = []
    dataobj = nsdf.EventData('spikes', unit='s', dtype=np.float32)
    source_name_dict = {}
    for ii in range(i_spikes):
        uid = 'nrn_'+str(ii)
        source_name_dict[uid] = uid
        dataobj.put_data(uid, Mi[ii])
        i_list.append(uid)
    source_ds = writer.add_event_ds_1d('inhibitory', 'spikes', i_list)
    writer.add_event_1d(source_ds, dataobj, source_name_dict)

#h5_vlen()
#h5_nan()
#h5_cmpd()
h5_vlen_nsdf()
h5_cmpd_nsdf()
h5_nan_nsdf()
# End of test_brian.py
