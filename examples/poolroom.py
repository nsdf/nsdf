from __future__ import division
from __future__ import print_function
from builtins import range

# poolroom.py --- 
# 
# Filename: poolroom.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Thu Jul 17 09:35:38 2014 (+0530)
# Version: 
# Last-Updated: Sun Jan 17 13:27:53 2016 (-0500)
#           By: subha
#     Update #: 3
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

import sys
sys.path.append('..')

"""Creates a sample NSDF file using objects inside a pool-room as example.

Example model suggested by: Matteo Cantarelli and Johannes Rieke.


leisurecenter (entity)
    poolroom (entity)
        area (static, value=100)
        table0 (entity)
            height (static, value=1.2)
            players (non-uniform, values=[2, 4, 6], times=[0.5, 1.3, 1.5])
            ball0 (entity)
                x (uniform, values=[1, 2, 3, 4, 5], time step=1)
                hit (event, values=[0.7, 0.8, 1.4])
            ball1 (entity)
                (same as ball0)
            ball2 (entity)
                (same as ball0)
        table1 (entity)
            (same as table0)

"""

__author__ = 'Subhasis Ray'

import h5py as h5
import numpy as np
from uuid import uuid1
import nsdf

def create_example():
    # First create the model tree
    model = nsdf.ModelComponent('LeisureCenter', uid=uuid1().hex)
    poolroom = nsdf.ModelComponent('PoolRoom', uid=uuid1().hex,
                                   parent=model)
    tables = []
    balls = []
    for ii in range(2):
        tables.append(nsdf.ModelComponent('table_{}'.format(ii),
                                          uid=uuid1().hex,
                                          parent=poolroom))
        for jj in range(3):
            balls.append(nsdf.ModelComponent('ball_{}'.format(jj),
                                       uid=uuid1().hex,
                                       parent=tables[-1]))
    id_path_dict = model.get_id_path_dict()
    path_id_dict = {value: key for key, value in id_path_dict.items()}

    # Create the NSDF writer object
    writer = nsdf.NSDFWriter('poolroom.h5', mode='w')
    writer.add_modeltree(model)
    dataobj = nsdf.StaticData('area', unit='m^2')
    dataobj.put_data(poolroom.uid, [100.0])
    source_ds = writer.add_static_ds('rooms', [poolroom.uid])
    writer.add_static_data(source_ds, dataobj)
    source_ds = writer.add_static_ds('tables', [tab.uid for tab in
                                                tables])
    dataobj = nsdf.StaticData('height', unit='m')
    for tab in tables:
        dataobj.put_data(tab.uid, 1.2)
    writer.add_static_data(source_ds, dataobj)
    source_ds = writer.add_nonuniform_ds_1d('tables', 'players',
                                           [tab.uid for tab in tables])
    dataobj = nsdf.NonuniformData('players', unit='item',
                                  tunit='hour', dtype=np.int32)
    for tab in tables:
        times = np.cumsum(np.random.exponential(1/10.0, size=10))
        dataobj.put_data(tab.uid, (np.random.randint(10, size=10),
                                   times))
    writer.add_nonuniform_1d(source_ds, dataobj, {tab.uid: tab.name
                                                  for tab in
                                                  tables})
    source_ds = writer.add_uniform_ds('balls', [ball.uid for ball in balls])
    dataobj = nsdf.UniformData('x', unit='cm')
    for ball in balls:
        dataobj.put_data(ball.uid, np.random.rand(10) * 10)
    dataobj.set_dt(1e-2, 's')    
    writer.add_uniform_data(source_ds, dataobj)
    
    source_ds = writer.add_event_ds_1d('balls', 'hit', [ball.uid for ball in balls])
    dataobj = nsdf.EventData('hit', unit='s')
    source_name_dict = {}
    for ball in balls:
        source_name_dict[ball.uid] = '{}_{}'.format(ball.name,
                                                    ball.uid)
        data = np.cumsum(np.random.exponential(1/100.0, size=10))
        dataobj.put_data(ball.uid, data)
    writer.add_event_1d(source_ds, dataobj, source_name_dict)
    
            
                      
    
    
if __name__ == '__main__':
    create_example()
    print('Finished')
    
# 
# poolroom.py ends here
