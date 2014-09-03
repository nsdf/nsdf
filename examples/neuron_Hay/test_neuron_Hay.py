# This script was written by Chaitanya Chintaluri c.chinaluri@nencki.gov.pl
# This software is available under GNU GPL3 License.

# Uses neuron simulator to dump the data into NSDF file format, using hdf5 
# using h5py. This was used to test various flavours of dumping the data
# while storing the currents, and voltage and spike times

# The model used was Layer 5 Pyramidal cell model (model db 139653) by
# Hay et.al. (2011)

# Requires neuron, h5py >= 2.3, matplotlib
# Run nrnivmodl mod_hay/
# Run python test_neuron_Hay.py 

from neuron import h
import matplotlib.pyplot as plt
import numpy as np
import sys

dump_hdf5 = True 
dump_type = 4 # use dump_type=4 for using NSDF library
# 1 = preference to time data.
# 2 = THIS IS NSDF. Agnostic of data 'addition of static subgroup'
# 3 = uses regional reference inside /model to point to specific data_sources
# 4 = uses NSDF library

#Obtain morphology details
n3dpoints = {} #has sec name and the first and last coordinates of its location
def retrieve_coordinate(sec):
    sec.push()
    x, y, z, d = [],[],[],[]
    area = 0
    tot_points = 0
    connect_next = False
    for i in range(int(h.n3d())):
        present = False
	x_i = h.x3d(i)
	y_i = h.y3d(i)
	z_i = h.z3d(i)
	d_i = h.diam3d(i)
	if x_i in x:
            ind = len(x) - 1 - x[::-1].index(x_i) # Getting the index of last value
	    if y_i == y[ind]:
                if z_i == z[ind]:
                    present = True
	if not present:
            k =(x_i, y_i, z_i)
	    x.append(x_i)
	    y.append(y_i)
	    z.append(z_i)
	    d.append(d_i)                
    h.pop_section()
    #adding num 3d points per section
    n3dpoints[sec.name()] = [np.array(x),np.array(y),np.array(z),np.array(d)]
    return (np.array(x),np.array(y),np.array(z),np.array(d))

#Load neuron file
h.load_file('Hay.hoc')

#Init dicts to save currents
i_dict = {}
sec_dict = {}
area_dict = {}
location_dict = {}
for sec in h.allsec():
    x,y,z,d = retrieve_coordinate(sec)
    t_segs = sec.nseg
    for seg_count,seg in enumerate(sec):
        #create vectors
        ina = h.Vector()
        ik = h.Vector()
        ica = h.Vector()
        ih = h.Vector()
        ih_iH = h.Vector()
        ik_bk = h.Vector()
        ik_sk = h.Vector()
        inf_sk = h.Vector()
        i_cap = h.Vector()
        i_pas = h.Vector()
        #record
        try:
            ina.record(seg._ref_ina) 
        except NameError:
            pass
        try:
            ik.record(seg._ref_ik) 
        except NameError:
            pass
        try:
           ica.record(seg._ref_ica)
        except NameError:
            pass
        try:
            ih.record(seg._ref_ihcn_Ih) 
        except NameError:
            pass
        #ih_iH.record(seg._ref_ik_K_Pst)
        #ik_bk.record(seg._ref_ik_K_Tst)
        #ik_sk.record(seg._ref_ik_SK_E2)
        #inf_sk.record(seg._ref_ik_SKv3_1)
        i_cap.record(seg._ref_i_cap) 
        i_pas.record(seg._ref_i_pas)        
        #place in dict
        factor1 = np.float32(seg_count)/t_segs
        factor2 = (np.float32(seg_count)+1.)/t_segs
        sp_name = str(sec.name()).rsplit('.')[-1]+"_"+str(seg_count)
        try:
            location_dict[sp_name] = [(x[-1]*factor1)+(x[0]*(1-factor1)), 
                                      (y[-1]*factor1)+(y[0]*(1-factor1)), 
                                      (z[-1]*factor1)+(z[0]*(1-factor1)), 
                                      (d[-1]*factor1)+(d[0]*(1-factor1)), 
                                      (x[-1]*factor2)+(x[0]*(1-factor2)), 
                                      (y[-1]*factor2)+(y[0]*(1-factor2)), 
                                      (z[-1]*factor2)+(z[0]*(1-factor2)),
                                      (d[-1]*factor2)+(d[0]*(1-factor2)), ]
        except IndexError: #no location specified
            location_dict[sp_name] = location_dict['soma[0]_0']#[0,0,0,0,0,0,0,0]
        i_dict[sp_name] = [ina, ik, ica, i_cap, i_pas, ih]
        sec_dict[sp_name] = sec
        area_dict[sp_name] = h.area( ((2.*seg_count)+1)/(2.*sec.nseg) )

#Default simulation parameters
thresh = -20
spikezaehler = h.NetCon(h.L5PCtemplate[0].soma[0](0.5)._ref_v, None, thresh, 0, 0)
spikes = h.Vector()
spikezaehler.record(spikes)
t_vec = h.Vector()
t_vec.record(h._ref_t)

#RUN SIMULATION
h.init()
h.run()

#CALCULATIONS BEFORE PLOTTING 
t_vec = np.array(t_vec)
n_i_dict = {}
time_vals = np.array(np.arange(0,600,0.25))
t_vec_l = len(time_vals)
for name, c_list in i_dict.iteritems(): #interpolating
    for ii,jj in enumerate(c_list):
        if np.array(jj).shape != (0,):
            c_list[ii] = np.interp(time_vals, t_vec, np.array(jj))            
        else:
            c_list[ii] = np.zeros((t_vec_l,), dtype=np.float32)
n_ina = np.zeros((t_vec_l))
n_ik = np.zeros((t_vec_l))
n_ica = np.zeros((t_vec_l))
n_i_cap = np.zeros((t_vec_l))
n_i_pas = np.zeros((t_vec_l))
n_ih = np.zeros((t_vec_l))
i_na_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_k_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_ca_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_ih_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_pas_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_cap_hdf5 = np.zeros((len(i_dict),t_vec_l), dtype=np.float32)
i_cp_names = []
doh_= 0
for name,c_list in i_dict.iteritems():
    i_vals = np.zeros((t_vec_l), dtype=np.float32)
    for ii in c_list:
        if np.array(ii).shape != (0,):
            i_vals += np.array(ii)
    n_i_dict[name] = i_vals
    this_sec = sec_dict[name]
    area_seg = h.area(0.5)
    if np.array(c_list[0]).shape != (0,):
        i_na_hdf5[doh_] = np.array(c_list[0])*area_seg
        n_ina += i_na_hdf5[doh_]
    else:
        i_na_hdf5[doh_] = np.zeros((t_vec_l,))

    if np.array(c_list[1]).shape != (0,):
        i_k_hdf5[doh_] = np.array(c_list[1])*area_seg
        n_ik += i_k_hdf5[doh_]
    else:
        i_k_hdf5[doh_] = np.zeros((t_vec_l,))

    if np.array(c_list[2]).shape != (0,):
        i_ca_hdf5[doh_] = np.array(c_list[2])*area_seg
        n_ica += i_ca_hdf5[doh_]
    else:
        i_ca_hdf5[doh_] = np.zeros((t_vec_l,))

    n_i_cap += np.array(c_list[3])*area_seg
    n_i_pas += np.array(c_list[4])*area_seg
    i_cap_hdf5[doh_] = np.array(c_list[3])*area_seg
    i_pas_hdf5[doh_] = np.array(c_list[4])*area_seg
    i_cp_names.append(name)
    if np.array(c_list[5]).shape != (0,):
        i_ih_hdf5[doh_] = np.array(c_list[5])*area_seg
        n_ih += i_ih_hdf5[doh_]
    else:
        i_ih_hdf5[doh_] = np.zeros((t_vec_l,))
    doh_ += 1

#coordinates of EPSP site
i_clamp_curr = np.interp(time_vals, t_vec, h.isoma)            
epsp_curr = np.interp(time_vals, t_vec, h.isyn)            
print 'epsp+dend site:', h.siteVec_a[0], h.siteVec_a[1]
print 'dend2 site:', h.siteVec_b[0], h.siteVec_b[1]
sec = h.L5PC.apic[int(h.siteVec_a[0])] #epsp + dend loc
t_seg = float(sec.nseg)
seg_num_a = int(t_seg*h.siteVec_a[1])
seg_num_b = int(t_seg*h.siteVec_b[1])
print seg_num_a, seg_num_b, int(t_seg)
x,y,z,d = retrieve_coordinate(sec)
factor1 = h.siteVec_a[1]
factor2 = 1.0 - h.siteVec_a[1]
epsp_location = [(x[-1]*factor1)+(x[0]*(1-factor1)), 
                 (y[-1]*factor1)+(y[0]*(1-factor1)), 
                 (z[-1]*factor1)+(z[0]*(1-factor1)), 
                 (d[-1]*factor1)+(d[0]*(1-factor1)), 
                 (x[-1]*factor2)+(x[0]*(1-factor2)), 
                 (y[-1]*factor2)+(y[0]*(1-factor2)), 
                 (z[-1]*factor2)+(z[0]*(1-factor2)),
                 (d[-1]*factor2)+(d[0]*(1-factor2)),]

#reformatting for hdf5 dump, and calc total currents
total_curr = np.zeros((t_vec_l,), dtype=np.float32)
total_hdf5 = np.zeros((len(n_i_dict), t_vec_l), dtype=np.float32)
curr_hdf5_names = []
for doh_, name in enumerate(i_cp_names):
    curr = n_i_dict[name]
    this_iter = curr*area_dict[name]*1e-2
    total_curr += this_iter
    total_hdf5[doh_] = this_iter

#changing from variable time step to constant time step
v_soma = np.interp(time_vals, t_vec, np.array(h.vsoma))
v_dend = np.interp(time_vals, t_vec, np.array(h.vdend))
v_dend2 = np.interp(time_vals, t_vec, np.array(h.vdend2))
v_all = np.vstack((v_soma, v_dend, v_dend2))

def tie_data_map(d_set, m_set, name, axis=0):
    d_set.dims[axis].label = name
    d_set.dims.create_scale(m_set, name)
    d_set.dims[axis].attach_scale(m_set)
    m_set.attrs.create('NAME', data='SOURCE')

def tie_data_map_extended(d_set, m_set, name, axis=0):
    d_set.dims[axis].label = name
    d_set.dims.create_scale(m_set, name)
    d_set.dims[axis].attach_scale(m_set)
    m_set.attrs.create('NAME', data='SOURCE')
    if axis==0:
        for idx, ii in enumerate(m_set):
            h5 = d_set.file
            path_, var_ = d_set.name.rsplit('/',1)
            h5.create_dataset('/model'+ path_ +'/'+str(ii)+'/'+var_, data=d_set.regionref[idx, :])
    elif axis==1:
        for idx, ii in enumerate(m_set):
            h5 = d_set.file
            path_, var_ = d_set.name.rsplit('/',1)
            #print '/model'+ path_ +'/'+str(ii)+'/'+var_
            h5.create_dataset('/model'+ path_ +'/'+str(ii)+'/'+var_, data=d_set.regionref[:, idx])
        
#Dump into HDF5
if dump_hdf5:
    import h5py
    if dump_type == 1:
    ### TYPE1
        h5 = h5py.File('Hay_currents_0.h5', 'a')
        currs_dset = h5.create_dataset('/data/uniform/hay/i', data=total_hdf5, dtype=np.float32)
        pas_dset = h5.create_dataset('/data/uniform/hay/i_pas', data=i_pas_hdf5, dtype=np.float32)
        cap_dset = h5.create_dataset('/data/uniform/hay/i_cap', data=i_cap_hdf5, dtype=np.float32)
        ca_dset = h5.create_dataset('/data/uniform/hay/i_ca', data=i_ca_hdf5, dtype=np.float32)
        na_dset = h5.create_dataset('/data/uniform/hay/i_na', data=i_na_hdf5, dtype=np.float32)
        k_dset = h5.create_dataset('/data/uniform/hay/i_k', data=i_k_hdf5, dtype=np.float32)
        ih_dset = h5.create_dataset('/data/uniform/hay/i_ih', data=i_ih_hdf5, dtype=np.float32)
        v_dset = h5.create_dataset('/data/uniform/hay/v', data=v_all, dtype=np.float32)
        iclamp_dset = h5.create_dataset('/data/uniform/electronics/i_clamp', data=i_clamp_curr*-1.0, dtype=np.float32)
        epsp_dset = h5.create_dataset('/data/uniform/electronics/epsp', data=epsp_curr, dtype=np.float32)
        spikes_dset = h5.create_dataset('/data/events/hay/spikes', data=spikes, dtype=np.float32)
        times_ds = h5.create_dataset('/map/time/uniform/time', data=time_vals, dtype=np.float32)
        cp_names = h5.create_dataset('/map/uniform/hay/names', data=i_cp_names)
        v_names = h5.create_dataset('/map/uniform/hay/v_names', data=['soma','dend', 'dend2'])
        events_names = h5.create_dataset('/map/events/hay/spike', data=['pyr_0'])
        tie_data_map(currs_dset, cp_names, 'SOURCE', 0)
        tie_data_map(pas_dset, cp_names, 'SOURCE', 0)
        tie_data_map(cap_dset, cp_names, 'SOURCE', 0)
        tie_data_map(ca_dset, cp_names, 'SOURCE', 0)
        tie_data_map(na_dset, cp_names, 'SOURCE', 0)
        tie_data_map(k_dset, cp_names, 'SOURCE', 0)
        tie_data_map(ih_dset, cp_names, 'SOURCE', 0)
        tie_data_map(v_dset, v_names, 'SOURCE', 0)
        tie_data_map(spikes_dset, events_names, 'SOURCE', 0)
        tie_data_map(currs_dset, times_ds, 'time', 1)
        tie_data_map(pas_dset, times_ds, 'time', 1)
        tie_data_map(cap_dset, times_ds, 'time', 1)
        tie_data_map(ca_dset, times_ds, 'time', 1)
        tie_data_map(na_dset, times_ds, 'time', 1)
        tie_data_map(k_dset, times_ds, 'time', 1)
        tie_data_map(ih_dset, times_ds, 'time', 1)
        tie_data_map(v_dset, times_ds, 'time', 1)
        tie_data_map(iclamp_dset, times_ds, 'time', 0)
        tie_data_map(epsp_dset, times_ds, 'time', 0)
        #morphology dump
        loc_array = np.zeros((len(location_dict), 8), dtype=np.float32)
        loc_names = []
        for doh_,name in enumerate(i_cp_names):
            loc_array[doh_] = np.array(location_dict[name])
            loc_names.append(name)
        morp_dset = h5.create_dataset('/model/morphology/hay', data=loc_array, dtype=np.float32)
        morp_names = h5.create_dataset('/model/morphology/hay_names', data=loc_names)
        morp_labels = h5.create_dataset('/model/dim_labels', data=['x0','y0','z0','d0','x1','y1','z1','d1'])
        tie_data_map(morp_dset, morp_names, 'SOURCE', 0)
        tie_data_map(morp_dset, morp_labels, 'label', 1)
        elec_dset = h5.create_dataset('/model/electronics/location', data=np.array((location_dict['soma[0]_0'], epsp_location)), dtype=np.float32)
        elec_names = h5.create_dataset('/model/electronics/names', data=['i_clamp', 'epsp_site'])
        tie_data_map(elec_dset, elec_names, 'SOURCE', 0)
        tie_data_map(elec_dset, morp_labels, 'label', 1)

    # ### TYPE2
    elif dump_type == 2:
        h5 = h5py.File('Hay_currents_0_2.h5', 'a')
        currs_dset = h5.create_dataset('/data/uniform/hay/i', data=total_hdf5, dtype=np.float32)
        pas_dset = h5.create_dataset('/data/uniform/hay/i_pas', data=i_pas_hdf5, dtype=np.float32)
        cap_dset = h5.create_dataset('/data/uniform/hay/i_cap', data=i_cap_hdf5, dtype=np.float32)
        ca_dset = h5.create_dataset('/data/uniform/hay/i_ca', data=i_ca_hdf5, dtype=np.float32)
        na_dset = h5.create_dataset('/data/uniform/hay/i_na', data=i_na_hdf5, dtype=np.float32)
        k_dset = h5.create_dataset('/data/uniform/hay/i_k', data=i_k_hdf5, dtype=np.float32)
        ih_dset = h5.create_dataset('/data/uniform/hay/i_ih', data=i_ih_hdf5, dtype=np.float32)
        v_dset = h5.create_dataset('/data/uniform/hay/v', data=v_all, dtype=np.float32)
        iclamp_dset = h5.create_dataset('/data/uniform/electronics/i_clamp', data=i_clamp_curr*-1.0, dtype=np.float32)
        epsp_dset = h5.create_dataset('/data/uniform/electronics/epsp', data=epsp_curr, dtype=np.float32)
        spikes_dset = h5.create_dataset('/data/events/hay/spikes', data=spikes, dtype=np.float32)
        times_ds = h5.create_dataset('/map/time', data=time_vals, dtype=np.float32)
        cp_names = h5.create_dataset('/map/hay_i_names', data=i_cp_names)
        v_names = h5.create_dataset('/map/hay_v_names', data=['soma','dend', 'dend2'])
        events_names = h5.create_dataset('/map/hay_spikes', data=['pyr_0'])
        tie_data_map(currs_dset, cp_names, 'SOURCE', 0)
        tie_data_map(pas_dset, cp_names, 'SOURCE', 0)
        tie_data_map(cap_dset, cp_names, 'SOURCE', 0)
        tie_data_map(ca_dset, cp_names, 'SOURCE', 0)
        tie_data_map(na_dset, cp_names, 'SOURCE', 0)
        tie_data_map(k_dset, cp_names, 'SOURCE', 0)
        tie_data_map(ih_dset, cp_names, 'SOURCE', 0)
        tie_data_map(v_dset, v_names, 'SOURCE', 0)
        tie_data_map(spikes_dset, events_names, 'SOURCE', 0)
        tie_data_map(currs_dset, times_ds, 'time', 1)
        tie_data_map(pas_dset, times_ds, 'time', 1)
        tie_data_map(cap_dset, times_ds, 'time', 1)
        tie_data_map(ca_dset, times_ds, 'time', 1)
        tie_data_map(na_dset, times_ds, 'time', 1)
        tie_data_map(k_dset, times_ds, 'time', 1)
        tie_data_map(ih_dset, times_ds, 'time', 1)
        tie_data_map(v_dset, times_ds, 'time', 1)
        tie_data_map(iclamp_dset, times_ds, 'time', 0)
        tie_data_map(epsp_dset, times_ds, 'time', 0)
        #morphology dump
        loc_array = np.zeros((len(location_dict), 8), dtype=np.float32)
        loc_names = []
        for doh_,name in enumerate(i_cp_names):
            loc_array[doh_] = np.array(location_dict[name])
            loc_names.append(name)
        morp_dset = h5.create_dataset('/data/static/morphology', data=loc_array, dtype=np.float32)
        #morp_names = h5.create_dataset('/map/morphology/hay_names', data=loc_names)
        morp_labels = h5.create_dataset('/map/morph_labels', data=['x0','y0','z0','d0','x1','y1','z1','d1'])
        tie_data_map(morp_dset, cp_names, 'SOURCE', 0)
        tie_data_map(morp_dset, morp_labels, 'label', 1)
        elec_dset = h5.create_dataset('/data/static/electronic_loc', data=np.array((location_dict['soma[0]_0'], epsp_location)), dtype=np.float32)
        elec_names = h5.create_dataset('/map/electronics_names', data=['i_clamp', 'epsp_site'])
        tie_data_map(elec_dset, elec_names, 'SOURCE', 0)
        tie_data_map(elec_dset, morp_labels, 'label', 1)

    elif dump_type == 4:
        sys.path.append('../../..')
        import nsdf
        writer = nsdf.NSDFWriter('hay_currents_nsdf.h5', mode='w')
        curr_source_ds = writer.add_uniform_ds('hay_currs', i_cp_names)
        data_obj_1 = nsdf.UniformData('i', unit='nA')
        data_obj_2 = nsdf.UniformData('i_pas', unit='nA')
        data_obj_3 = nsdf.UniformData('i_cap', unit='nA')
        data_obj_4 = nsdf.UniformData('i_ca', unit='nA')
        data_obj_5 = nsdf.UniformData('i_na', unit='nA')
        data_obj_6 = nsdf.UniformData('i_k', unit='nA')
        data_obj_7 = nsdf.UniformData('i_ih', unit='nA')

        for ii,source in enumerate(i_cp_names):
            data_obj_1.put_data(source, total_hdf5[ii])
            data_obj_2.put_data(source, i_pas_hdf5[ii])
            data_obj_3.put_data(source, i_cap_hdf5[ii])
            data_obj_4.put_data(source, i_ca_hdf5[ii])
            data_obj_5.put_data(source, i_na_hdf5[ii])
            data_obj_6.put_data(source, i_k_hdf5[ii])
            data_obj_7.put_data(source, i_ih_hdf5[ii])
        data_obj_1.set_dt(0.25, unit='ms')
        data_obj_2.set_dt(0.25, unit='ms')
        data_obj_3.set_dt(0.25, unit='ms')
        data_obj_4.set_dt(0.25, unit='ms')
        data_obj_5.set_dt(0.25, unit='ms')
        data_obj_6.set_dt(0.25, unit='ms')
        data_obj_7.set_dt(0.25, unit='ms')
    
        v_source_ds = writer.add_uniform_ds('hay_v', ['soma','dend', 'dend2'])
        ele_source_ds = writer.add_uniform_ds('hay_ele', ['iclamp','epsp'])
        data_obj_8 = nsdf.UniformData('v', unit='mV')
        for ii,source in enumerate(['soma','dend', 'dend2']):
            data_obj_8.put_data(source, v_all[ii])
        data_obj_9 = nsdf.UniformData('electronics', unit='nA')
        data_obj_9.put_data('iclamp', i_clamp_curr*-1.)
        data_obj_9.put_data('epsp', epsp_curr)

        data_obj_8.set_dt(0.25, unit='ms')
        data_obj_9.set_dt(0.25, unit='ms')

        writer.add_uniform_data(curr_source_ds, data_obj_1)
        writer.add_uniform_data(curr_source_ds, data_obj_2)
        writer.add_uniform_data(curr_source_ds, data_obj_3)
        writer.add_uniform_data(curr_source_ds, data_obj_4)
        writer.add_uniform_data(curr_source_ds, data_obj_5)
        writer.add_uniform_data(curr_source_ds, data_obj_6)
        writer.add_uniform_data(curr_source_ds, data_obj_7)

        writer.add_uniform_data(v_source_ds, data_obj_8)
        writer.add_uniform_data(ele_source_ds, data_obj_9)


        # for doh_,name in enumerate(i_cp_names):
        #     loc_array[doh_] = np.array(location_dict[name])
        #     loc_names.append(name)
        # morp_dset = h5.create_dataset('/data/static/morphology', data=loc_array, dtype=np.float32)
        # #morp_names = h5.create_dataset('/map/morphology/hay_names', data=loc_names)
        # morp_labels = h5.create_dataset('/map/morph_labels', data=['x0','y0','z0','d0','x1','y1','z1','d1'])
        # tie_data_map(morp_dset, cp_names, 'SOURCE', 0)
        # tie_data_map(morp_dset, morp_labels, 'label', 1)
        # elec_dset = h5.create_dataset('/data/static/electronic_loc', data=np.array((location_dict['soma[0]_0'], epsp_location)), dtype=np.float32)
        # elec_names = h5.create_dataset('/map/electronics_names', data=['i_clamp', 'epsp_site'])
        # tie_data_map(elec_dset, elec_names, 'SOURCE', 0)
        # tie_data_map(elec_dset, morp_labels, 'label', 1)

    ### TYPE 3
    elif dump_type == 3:
        h5 = h5py.File('Hay_currents_0_3.h5', 'a')
        currs_dset = h5.create_dataset('/data/uniform/hay/i', data=total_hdf5, dtype=np.float32)
        pas_dset = h5.create_dataset('/data/uniform/hay/i_pas', data=i_pas_hdf5, dtype=np.float32)
        cap_dset = h5.create_dataset('/data/uniform/hay/i_cap', data=i_cap_hdf5, dtype=np.float32)
        ca_dset = h5.create_dataset('/data/uniform/hay/i_ca', data=i_ca_hdf5, dtype=np.float32)
        na_dset = h5.create_dataset('/data/uniform/hay/i_na', data=i_na_hdf5, dtype=np.float32)
        k_dset = h5.create_dataset('/data/uniform/hay/i_k', data=i_k_hdf5, dtype=np.float32)
        ih_dset = h5.create_dataset('/data/uniform/hay/i_ih', data=i_ih_hdf5, dtype=np.float32)
        v_dset = h5.create_dataset('/data/uniform/hay/v', data=v_all, dtype=np.float32)
        iclamp_dset = h5.create_dataset('/data/uniform/electronics/i_clamp', data=i_clamp_curr*-1.0, dtype=np.float32)
        epsp_dset = h5.create_dataset('/data/uniform/electronics/epsp', data=epsp_curr, dtype=np.float32)
        #spikes_dset = h5.create_dataset('/data/events/hay/spikes', data=spikes, dtype=np.float32)
        times_ds = h5.create_dataset('/map/common/time', data=time_vals, dtype=np.float32)
        cp_names = h5.create_dataset('/map/common/hay_names', data=i_cp_names)
        v_names = h5.create_dataset('/map/uniform/hay/v_names', data=['soma','dend', 'dend2'])
        events_names = h5.create_dataset('/map/events/hay/hay_spike', data=['pyr_0'])
        tie_data_map_extended(currs_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(pas_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(cap_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(ca_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(na_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(k_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(ih_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(v_dset, v_names, 'SOURCE', 0)
        #tie_data_map_extended(spikes_dset, events_names, 'SOURCE', 0)
        tie_data_map_extended(currs_dset, times_ds, 'time', 1)
        tie_data_map_extended(pas_dset, times_ds, 'time', 1)
        tie_data_map_extended(cap_dset, times_ds, 'time', 1)
        tie_data_map_extended(ca_dset, times_ds, 'time', 1)
        tie_data_map_extended(na_dset, times_ds, 'time', 1)
        tie_data_map_extended(k_dset, times_ds, 'time', 1)
        tie_data_map_extended(ih_dset, times_ds, 'time', 1)
        tie_data_map_extended(v_dset, times_ds, 'time', 1)
        tie_data_map_extended(iclamp_dset, times_ds, 'time', 0)
        tie_data_map_extended(epsp_dset, times_ds, 'time', 0)
        #morphology dump
        loc_array = np.zeros((len(location_dict), 8), dtype=np.float32)
        loc_names = []
        for doh_,name in enumerate(i_cp_names):
            loc_array[doh_] = np.array(location_dict[name])
            loc_names.append(name)
        morp_dset = h5.create_dataset('/data/static/hay_morph', data=loc_array, dtype=np.float32)
        #morp_names = h5.create_dataset('/map/common/hay_names', data=loc_names)
        morp_labels = h5.create_dataset('/map/static/dim_labels', data=['x0','y0','z0','d0','x1','y1','z1','d1'])
        tie_data_map_extended(morp_dset, cp_names, 'SOURCE', 0)
        tie_data_map_extended(morp_dset, morp_labels, 'label', 1)
        elec_dset = h5.create_dataset('/data/static/elec_loc', data=np.array((location_dict['soma[0]_0'], epsp_location)), dtype=np.float32)
        elec_names = h5.create_dataset('/map/static/ele_names', data=['i_clamp', 'epsp_site'])
        tie_data_map_extended(elec_dset, elec_names, 'SOURCE', 0)
        tie_data_map_extended(elec_dset, morp_labels, 'label', 1)
    h5.close()

#PLOTTING    
plt.hold(True)
plt.subplot(311)
plt.plot(time_vals, v_soma , label='soma')
plt.plot(time_vals, v_dend, label='dend')
plt.plot(time_vals, v_dend2, label='dend2')
plt.plot(spikes, [1.0]*len(spikes), 'ro', label = 'spikes')
plt.legend()

plt.subplot(312)
plt.plot(time_vals, total_curr, label='tot_i_Hay')
try:
    plt.plot(time_vals, epsp_curr, label='apic_epsp')
except NameError:
    print 'No vector for apical'
    pass
try:
    plt.plot(time_vals, -1.0*i_clamp_curr, label='i_clamp')
except NameError:
    print 'No vector for i clamp'
    pass
plt.legend()

plt.subplot(313)
plt.plot(time_vals, n_i_cap*1e-2, label='i_cap')
plt.plot(time_vals, n_i_pas*1e-2, label='i_pas')
plt.legend()
plt.show()

# End of test_neuron_Hay.py 
