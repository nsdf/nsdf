# test_nsdfwriter.py --- 
# 
# Filename: test_nsdfwriter.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Fri Apr 25 22:22:27 2014 (+0530)
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
"""Test code for NSDFWriter.

Using Subhasis' custom format used for saving Traub et al 2005 data
and visualizing the same in dataviz.

"""

import sys
from collections import defaultdict
import numpy as np
import h5py as h5
sys.path.append('..')
import nsdf
from datetime import datetime

dtype=np.float32

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print """Usage: %s sourcefile targetfile {dialect} {compress}
        convert sourcefile in dataviz format to targetfile in NSDF format.""" % (sys.argv[0])
        sys.exit(1)
    if len(sys.argv) > 3:
        dialect = sys.argv[3]
    else:
        dialect = '1d'
    if (len(sys.argv) > 4) and eval(sys.argv[4]):
        compression = 'gzip'
        compression_opts = 6
        fletcher32 = True
        shuffle = True
    else:
        compression = None
        compression_opts = None
        fletcher32 = False
        shuffle = False
        
    fd = h5.File(sys.argv[1], 'r')
    vm_dict = defaultdict(dict)
    for cellname, vm_array in fd['/Vm'].items():
        cellclass = cellname.split('_')[0]
        vm_dict[cellclass][cellname] = vm_array

    spike_dict = defaultdict(dict)
    for cellname, spiketrain in fd['/spikes'].items():
        cellclass = cellname.split('_')[0]
        spike_dict[cellclass][cellname] = spiketrain
    tstart = datetime.now()
    nsdf_writer = nsdf.writer(sys.argv[2])
    for cellclass, celldict in vm_dict.items():
        data_array = np.vstack(celldict.values())
        nsdf_writer.add_uniform_dataset('%s_Vm' % (cellclass), data_array, 'Vm',
                                        sourcelist=celldict.keys(),
                                        t_end=fd.attrs['simtime'],
                                        dtype=dtype,
                                        compression=compression,
                                        compression_opts=compression_opts,
                                        shuffle=shuffle,
                                        fletcher32=fletcher32)
        # The following is a dummy case with separate time arrays for each dataset - as if it were nonuniform data
        dataset_names = None if dialect != '1d' else celldict.keys()
        times = [np.linspace(0, float(fd.attrs['simtime']), data_array.shape[1])] * data_array.shape[1]
        nsdf_writer.add_nonuniform_dataset('%s_Vm' % (cellclass), data_array, 'Vm',
                                           times,
                                           dataset_names=dataset_names,
                                           sourcelist=celldict.keys(),
                                           dialect=dialect,
                                           dtype=dtype,
                                           compression=compression,
                                           compression_opts=compression_opts,
                                           shuffle=shuffle,
                                           fletcher32=fletcher32)
    for cellclass, celldict in spike_dict.items():
        # Here we try to name the datasets by the index of the source
        # so that there is a one-to-one mapping between sourcelist and
        # datasets.
        dataset_names = None if dialect != '1d' else ['%d' % n for n in range(len(celldict))]
        nsdf_writer.add_spiketrains(cellclass,
                                    celldict.values(),
                                    dataset_names=dataset_names,
                                    sourcelist=celldict.keys(), 
                                    dialect=dialect,
                                    dtype=dtype,
                                    compression=compression,
                                    compression_opts=compression_opts,
                                    shuffle=shuffle,
                                    fletcher32=fletcher32)
    tend = datetime.now()
    dt = tend - tstart
    print 'time to write entire file: %g s' % (dt.days * 86400 + dt.seconds + 1e-6 * dt.microseconds)
    
    

# 
# test_nsdfwriter.py ends here
