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


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print """Usage: %s sourcefile targetfile
        convert sourcefile in dataviz format to targetfile in NSDF format.""" % (sys.argv[0])
        sys.exit(1)
    if len(sys.argv) > 3:
        vlen = eval(sys.argv[3])
    fd = h5.File(sys.argv[1], 'r')
    vm_dict = defaultdict(dict)
    for cellname, vm_array in fd['/Vm'].items():
        cellclass = cellname.split('_')[0]
        vm_dict[cellclass][cellname] = vm_array

    spike_dict = defaultdict(dict)
    for cellname, spiketrain in fd['/spikes'].items():
        cellclass = cellname.split('_')[0]
        spike_dict[cellclass][cellname] = spiketrain
        
    nsdf_writer = nsdf.writer(sys.argv[2])
    for cellclass, celldict in vm_dict.items():
        data_array = np.vstack(celldict.values())
        nsdf_writer.add_uniform_dataset('%s_Vm' % (cellclass), data_array, 'Vm',
                                        sourcelist=celldict.keys(),
                                        t_end=fd.attrs['simtime'])
    for cellclass, celldict in spike_dict.items():
        # Here we try to name the datasets by the index of the source
        # so that there is a one-to-one mapping between sourcelist and
        # datasets.
        dataset_names = None if vlen else ['%d' % n for n in range(len(celldict))]
        nsdf_writer.add_spiketrains(cellclass, celldict.values(),
                                    dataset_names,
                                    sourcelist=celldict.keys())
    
    

# 
# test_nsdfwriter.py ends here
