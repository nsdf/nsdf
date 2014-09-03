# benchmark_traub_data.py --- 
# 
# Filename: benchmark_traub_data.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Sep  1 17:18:51 2014 (+0530)
# Version: 
# Last-Updated: 
#           By: 
#     Update #: 0
# URL: 
# Keywords: 
# Compatibility: 
# 
# 

# Commentary: 
# 
# 
# 
# 

# Change log:
# 
# 
# 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA.
# 
# 

# Code:
"""This script is for benchmarking the NSDF writer with typical
neuroscience simulation data.

It does the following: load data from a Traub 2005 simulation by
Subhasis. This file is in another HDF5 format and large (~500M).

"""
import os
import sys
import h5py as h5
import numpy as np

sys.path.append('..')
import nsdf

INCREMENTAL_STEP = 1024
DATAFILE = 'data_20120522_152734_10973.h5'
DATADIR = '/data/subha/nsdf_samples/benchmark'

def read_data():
    """Read the file contents in custom format. This format has the following groups:

    /Ca : Group containing [Ca2+] in mM of a fraction of the
          cells. Each dataset is named after the cell it is recorded
          from.

    /Vm : Group containing Vm in Volt.

    /bias_current : Group containing bias currents for each
                    celltype. This is a step current injection applied to all the
                    cells of that type.

    /ectopic_spikes : These are Poisson spikes delivered to some of
                      the cell types synaptically. The datasets are
                      named like: ectopic_{cellname}

    /lfp : Local field potential recorded from pyramidal cells. These
           datasets are named like: electrode_{depth}{unit}. Also LFP
           calculation algorithm has been applied to compute the
           contribution of specific subtypes of pyramidal cells and
           these are named electrode_{depth}{unit}_{celltype}.

    /runconfig : This contains compound datasets storing the runtime
                 configurations. Only part of this information is
                 relevant for NSDF.

    /spikes : contains spike trains for all the cells. Each dataset is
              named after the cell it is recorded from.

    /stimulus : contains current pulse stimulus applied to TCR
                cells. There three datasets here: stim_bg - a
                background stimulus. stim_probe : a probe stimulus
                that is applied with every alternate background
                stimulus. stim_gate : for gating the two stimuli.

    /synapse : contains Gk of some synapses. The datasets are named
               like
               gk_{postsynaptic_cell}_{postsynaptic_compartment}_{synapse_type}_from_{source_celltype}
               
    All continuous data are uniformly sampled.

    """
    with h5.File(os.path.join(DATADIR, DATAFILE), 'r') as datafile:
        ca = {str(key): np.asarray(value, dtype=np.float64) for key, value
              in datafile['Ca'].items()}
        Vm = {str(key): np.asarray(value, dtype=np.float64) for key, value
              in datafile['Vm'].items()}
        lfp = {str(key): np.asarray(value, dtype=np.float64) for key, value
               in datafile['lfp'].items()}
        spike = {str(key): np.asarray(value, dtype=np.float32) for key, value
                 in datafile['spikes'].items()}
        cell_ids = [str(key) for key in spike.keys()]
        electrode_ids = [str(key) for key in lfp.keys()]
        schedinfo = dict(datafile['runconfig/scheduling'])
        simtime = float(schedinfo['simtime'])
        plotdt = float(schedinfo['plotdt'])
        return {'cell_ids': cell_ids,
                'electrode_ids': electrode_ids,
                'spike': spike,
                'ca': ca,
                'Vm': Vm,
                'lfp': lfp,
                'dt': plotdt,    # note that stim has a difrferent dt
                'simtime': simtime}

DATA = read_data()
ca_data = nsdf.UniformData('Ca', field='conc', unit='mM',
                               dt=DATA['dt'], tunit='s')
ca_data.update_source_data_dict(DATA['ca'])
Vm_data = nsdf.UniformData('Vm', field='Vm', unit='V', dt=DATA['dt'],
                           tunit='s')
Vm_data.update_source_data_dict(DATA['Vm'])
spike_data = nsdf.EventData('spike', field='spiketime', unit='s', dtype=np.float32)
spike_data.update_source_data_dict(DATA['spike'])


def benchmark_write_oned(**kwargs):
    """Write LFP, Vm, spike trains, and any other data."""
    compression = kwargs.get('compression', '')
    filename = '{}_ONED_{}.h5'.format(DATAFILE.split('.')[0],
                                  compression)
    filepath = os.path.join(DATADIR, filename)
    writer = nsdf.NSDFWriter(filepath, mode='w',
                             dialect=nsdf.dialect.ONED, **kwargs)
    cont_rec_sources = writer.add_uniform_ds('continuous_recorded',
                                             ca_data.get_sources())
    writer.add_uniform_data(cont_rec_sources, ca_data)
    writer.add_uniform_data(cont_rec_sources, Vm_data)
    spike_sources = writer.add_event_ds_1d('all_cells', 'spike',
                                           spike_data.get_sources())
    writer.add_event_1d(spike_sources, spike_data)    

    
def benchmark_write_vlen(**kwargs):
    compression = kwargs.get('compression', '')
    filename = '{}_VLEN_{}.h5'.format(DATAFILE.split('.')[0],
                                           compression)
    filepath = os.path.join(DATADIR, filename)
    writer = nsdf.NSDFWriter(filepath, mode='w', dialect=nsdf.dialect.VLEN,
                             **kwargs)
    cont_rec_sources = writer.add_uniform_ds('continuous_recorded',
                                             ca_data.get_sources())
    writer.add_uniform_data(cont_rec_sources, ca_data, fixed=True)
    writer.add_uniform_data(cont_rec_sources, Vm_data, fixed=True)
    spike_sources = writer.add_event_ds('all_cells', spike_data.get_sources())
    writer.add_event_vlen(spike_sources, spike_data, fixed=True)    


def benchmark_write_nanpadded(**kwargs):
    compression = kwargs.get('compression', '')
    filename = '{}_NAN_{}.h5'.format(DATAFILE.split('.')[0],
                                          compression)
    filepath = os.path.join(DATADIR, filename)    
    writer = nsdf.NSDFWriter(filepath, mode='w',
                             dialect=nsdf.dialect.VLEN, **kwargs)
    cont_rec_sources = writer.add_uniform_ds('continuous_recorded',
                                             ca_data.get_sources())
    writer.add_uniform_data(cont_rec_sources, ca_data, fixed=True)
    writer.add_uniform_data(cont_rec_sources, Vm_data, fixed=True)
    spike_sources = writer.add_event_ds('all_cells', spike_data.get_sources())
    writer.add_event_vlen(spike_sources, spike_data, fixed=True)

    
def benchmark_write_oned_incremental(**kwargs):
    compression = kwargs.get('compression', '')
    prefix = DATAFILE.split('.')[0]
    filename = '{}_ONED_{}_incr.h5'.format(prefix, compression)
    filepath = os.path.join(DATADIR, filename)
    writer = nsdf.NSDFWriter(filepath, dialect=nsdf.dialect.ONED,
                             mode='w', **kwargs)
    cont_src = writer.add_uniform_ds('continuous_recorded',
                                     ca_data.get_sources())
    spike_sources = writer.add_event_ds_1d('all_cells', 'spike',
                                           spike_data.get_sources())
    for ii in range(0, int(DATA['simtime']/DATA['dt'] + 0.5) +
                    INCREMENTAL_STEP/2, INCREMENTAL_STEP):
        ca_data_tmp = nsdf.UniformData(ca_data.name,
                                       unit=ca_data.unit,
                                       dt=ca_data.dt,
                                       tunit=ca_data.tunit)
        for src, data in ca_data.get_source_data_dict().items():
            ca_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, ca_data_tmp)
        Vm_data_tmp = nsdf.UniformData(Vm_data.name,
                                       unit=Vm_data.unit,
                                       dt=Vm_data.dt,
                                       tunit=Vm_data.tunit)
        for src, data in Vm_data.get_source_data_dict().items():
            Vm_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, Vm_data_tmp)
        tstart = ii * Vm_data.dt
        tend = (ii + INCREMENTAL_STEP) * Vm_data.dt
        spike_data_tmp = nsdf.EventData(spike_data.name,
                                        unit=spike_data.unit,
                                        dtype=spike_data.dtype)
        for src, data in spike_data.get_source_data_dict().items():
            spike_data_tmp.put_data(src,
                                    data[(data >= tstart) & (data < tend)])
        writer.add_event_1d(spike_sources, spike_data_tmp)


def benchmark_write_vlen_incremental(**kwargs):
    compression = kwargs.get('compression', '')
    prefix = DATAFILE.split('.')[0]
    filename = '{}_VLEN_{}_incr.h5'.format(prefix, compression)
    filepath = os.path.join(DATADIR, filename)
    writer = nsdf.NSDFWriter(filepath, dialect=nsdf.dialect.VLEN,
                             mode='w', **kwargs)
    cont_src = writer.add_uniform_ds('continuous_recorded',
                                     ca_data.get_sources())
    spike_sources = writer.add_event_ds('all_cells',
                                        spike_data.get_sources())
    for ii in range(0, int(DATA['simtime']/DATA['dt'] + 0.5) +
                    INCREMENTAL_STEP/2, INCREMENTAL_STEP):
        ca_data_tmp = nsdf.UniformData(ca_data.name,
                                       unit=ca_data.unit,
                                       dt=ca_data.dt,
                                       tunit=ca_data.tunit)
        for src, data in ca_data.get_source_data_dict().items():
            ca_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, ca_data_tmp)
        Vm_data_tmp = nsdf.UniformData(Vm_data.name,
                                       unit=Vm_data.unit,
                                       dt=Vm_data.dt,
                                       tunit=Vm_data.tunit)
        for src, data in Vm_data.get_source_data_dict().items():
            Vm_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, Vm_data_tmp)
        tstart = ii * Vm_data.dt
        tend = (ii + INCREMENTAL_STEP) * Vm_data.dt
        spike_data_tmp = nsdf.EventData(spike_data.name,
                                        unit=spike_data.unit,
                                        dtype=spike_data.dtype)
        for src, data in spike_data.get_source_data_dict().items():
            spike_data_tmp.put_data(src,
                                    data[(data >= tstart) & (data < tend)])
        writer.add_event_vlen(spike_sources, spike_data_tmp)


def benchmark_write_nan_incremental(**kwargs):
    compression = kwargs.get('compression', '')
    prefix = DATAFILE.split('.')[0]
    filename = '{}_NAN_{}_incr.h5'.format(prefix, compression)
    filepath = os.path.join(DATADIR, filename)
    writer = nsdf.NSDFWriter(filepath, dialect=nsdf.dialect.NANPADDED,
                             mode='w', **kwargs)
    cont_src = writer.add_uniform_ds('continuous_recorded',
                                     ca_data.get_sources())
    spike_sources = writer.add_event_ds('all_cells',
                                        spike_data.get_sources())
    for ii in range(0, int(DATA['simtime']/DATA['dt'] + 0.5) +
                    INCREMENTAL_STEP/2, INCREMENTAL_STEP):
        ca_data_tmp = nsdf.UniformData(ca_data.name,
                                       unit=ca_data.unit,
                                       dt=ca_data.dt,
                                       tunit=ca_data.tunit)
        for src, data in ca_data.get_source_data_dict().items():
            ca_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, ca_data_tmp)
        Vm_data_tmp = nsdf.UniformData(Vm_data.name,
                                       unit=Vm_data.unit,
                                       dt=Vm_data.dt,
                                       tunit=Vm_data.tunit)
        for src, data in Vm_data.get_source_data_dict().items():
            Vm_data_tmp.put_data(src, data[ii:ii+INCREMENTAL_STEP])
        writer.add_uniform_data(cont_src, Vm_data_tmp)
        tstart = ii * Vm_data.dt
        tend = (ii + INCREMENTAL_STEP) * Vm_data.dt
        spike_data_tmp = nsdf.EventData(spike_data.name,
                                        unit=spike_data.unit,
                                        dtype=spike_data.dtype)
        for src, data in spike_data.get_source_data_dict().items():
            spike_data_tmp.put_data(src,
                                    data[(data >= tstart) & (data < tend)])
        writer.add_event_nan(spike_sources, spike_data_tmp)


def benchmark_read_oned(compressed):
    pass

def benchmark_read_vlen(compressed):
    pass

def benchmark_read_nanpadded(compressed):
    pass


def benchmark_write_oned_compressed():
    benchmark_write_oned(compression='gzip', compression_opts=6, fletcher32=True, shuffle=True)


def benchmark_write_oned_uncompressed():
    benchmark_write_oned()


def benchmark_write_vlen_compressed():
    benchmark_write_vlen(compression='gzip', compression_opts=6, fletcher32=True, shuffle=True)


def benchmark_write_vlen_uncompressed():
    benchmark_write_vlen()


def benchmark_write_nan_compressed():
    benchmark_write_nanpadded(compression='gzip', compression_opts=6, fletcher32=True, shuffle=True)


def benchmark_write_nan_uncompressed():
    benchmark_write_nanpadded()

def benchmark_write_oned_incr_uncompressed():
    benchmark_write_oned_incremental()

def benchmark_write_oned_incr_compressed():
    benchmark_write_oned_incremental(compression='gzip',
                                     compression_opts=6,
                                     fletcher32=True, shuffle=True)

def benchmark_write_nan_incr_uncompressed():
    benchmark_write_nan_incremental()

def benchmark_write_nan_incr_compressed():
    benchmark_write_nan_incremental(compression='gzip',
                                     compression_opts=6,
                                     fletcher32=True, shuffle=True)
def benchmark_write_vlen_incr_uncompressed():
    benchmark_write_vlen_incremental()

def benchmark_write_vlen_incr_compressed():
    benchmark_write_vlen_incremental(compression='gzip',
                                     compression_opts=6,
                                     fletcher32=True, shuffle=True)
    
    
@profile
def main():
    # Immediate writing
    benchmark_write_oned_compressed()
    benchmark_write_oned_uncompressed()
    benchmark_write_vlen_compressed()
    benchmark_write_vlen_uncompressed()
    benchmark_write_nan_compressed()
    benchmark_write_nan_uncompressed()
    # Incremental writing
    benchmark_write_oned_incr_uncompressed()
    benchmark_write_oned_incr_compressed()
    benchmark_write_nan_incr_uncompressed()
    benchmark_write_nan_incr_compressed()
    benchmark_write_vlen_incr_uncompressed()
    benchmark_write_vlen_incr_compressed()
    

if __name__ == '__main__':
    main()

# 
# benchmark_traub_data.py ends here
