# model_description_example.py --- 
# 
# Filename: model_description_example.py
# Description: 
# Author: subha
# Maintainer: 
# Created: Fri Jul 11 23:22:55 2014 (+0530)
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
__author__ = 'Subhasis Ray'

import numpy as np
import h5py as h5

def create_example_model_0(filename='model0.h5'):
    """This is the dumbest model we could think of. We simulate a
    single compartmental neuron model and record the membrane
    potential Vm of this model.
    """
    datalen = 1000
    fd = h5.File(filename, 'w')
    data_group = fd.create_group('/data')
    map_group = fd.create_group('/map')
    model_group = fd.create_group('/model')
    population = model_group.create_group('population')
    cell_model = population.create_group('cell')
    cell_data = data_group.create_group('uniform')
    cell_data_pop = cell_data.create_group('cell')
    cell_data_pop['Vm'] = np.asarray(np.random.rand(1, datalen), dtype='f8')
    map_src = map_group.create_group('source')
    uniform_src  = map_src.create_group('uniform')
    map_uniform_cell_pop = uniform_src.create_dataset('cell', data=[['cell']])
    cell_data_pop['Vm'].dims.create_scale(map_uniform_cell_pop, 'source')
    cell_data_pop['Vm'].dims[0].attach_scale(map_uniform_cell_pop)
    dtype = h5.special_dtype(ref=h5.Reference)
    attr = np.empty((1,), dtype=dtype)
    attr[:] = [map_uniform_cell_pop.ref]
    dmap = cell_model.attrs['datamap'] = attr
    map_uniform_cell_pop.attrs['model'] = cell_model
    fd.close()

if __name__ == '__main__':

    create_example_model_0()
    
    


# 
# model_description_example.py ends here
