# poolroom.py --- 
# 
# Filename: poolroom.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Thu Jul 17 09:35:38 2014 (+0530)
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

import h5py as h5
import numpy as np

VLENSTR = h5.special_dtype(vlen=str)
VLENFLOAT = h5.special_dtype(vlen='float32')
OBJECTREF = h5.special_dtype(ref=h5.Reference)

SAMPLING_TYPES = ['uniform', 'nonuniform', 'event', 'static']

def create_example():
    with h5.File('poolroom.h5', 'w') as fd:
        model = fd.create_group('/model')
        data = fd.create_group('/data')
        mapping = fd.create_group('/map')
        time_grp = mapping.create_group('time')
        dgrp = {}
        mgrp = {}
        for sampling in SAMPLING_TYPES:
            dgrp[sampling] = data.create_group(sampling)
            mgrp[sampling] = mapping.create_group(sampling)
        modeltree = model.create_group('modeltree')
        # 'components' simpler than 'entities'?
        entities = modeltree.create_dataset('entities', shape=(1,1),
                                            data=['{}/leisurecenter'.format(
                                                modeltree.name)],
                                            dtype=VLENSTR)
        lc = modeltree.create_group('leisurecenter')
        lc.attrs['uid'] = lc.name
        entities = lc.create_dataset('entities', shape=(1,1),
                                     data=['{}/poolroom'.format(lc.name)],
                                     dtype=VLENSTR)
        lc_map = mgrp['static'].create_dataset('leisurecenter', shape=(1,1),
                                               data =[entities[0]], dtype=VLENSTR)
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] = lc.ref
        # model -> map
        map_ref = np.empty((1,), dtype=OBJECTREF)
        map_ref[0] = lc_map.ref    
        lc.attrs['map'] = map_ref

        lc_data = dgrp['static'].create_group('leisurecenter')
        area = lc_data.create_dataset('area', data=[100.0], dtype='float64')
        area.attrs['field'] = 'area'
        area.attrs['unit'] = 'm^2'
        area.dims.create_scale(lc_map, 'source')
        area.dims[0].attach_scale(lc_map)
        area.dims[0].label = 'source'

        pr = lc.create_group('poolroom')
        pr.attrs['uid'] = pr.name
        entities = pr.create_dataset('entities', shape=(2,1),
                                     data=['{}/table0'.format(pr.name),
                                           '{}/table1'.format(pr.name)],
                                     dtype=VLENSTR)    
        pr_map = mgrp['static'].create_dataset('poolroom',
                                               data=[entity for entity in entities],
                                               dtype=VLENSTR)
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] =  pr.ref
        pr_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1,), dtype=OBJECTREF)
        map_ref[0] = pr_map.ref
        pr.attrs['map'] = map_ref

        pr_data = dgrp['static'].create_group('poolroom')
        height = pr_data.create_dataset('height', data=[1.2, 1.2])
        height.attrs['field'] = 'height'
        height.attrs['unit'] = 'm'
        height.dims.create_scale(pr_map, 'source')
        height.dims[0].attach_scale(pr_map)
        height.dims[0].label = 'source'

        pr_map = mgrp['nonuniform'].create_dataset('poolroom',
                                                   data=[entity for entity in entities],
                                                   dtype=VLENSTR)
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] =  pr.ref
        pr_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1 + len(pr.attrs['map']),), dtype=OBJECTREF)
        map_ref[-1] = pr_map.ref
        map_ref[:-1] = pr.attrs['map']
        pr.attrs['map'] = map_ref
        pr_data = dgrp['nonuniform'].create_group('poolroom')
        players = pr_data.create_dataset('players',
                                         data = [[2, 4, 6], [2, 4, 6]],
                                         shape=(2, 3), dtype='u8')
        players.attrs['field'] = 'players'
        players.attrs['unit'] = 'item' # SBML unit
        players.dims.create_scale(pr_map, 'source')
        players.dims[0].attach_scale(pr_map)
        players.dims[0].label = 'source'
        pr_time = time_grp.create_dataset('tplayers', data=[0.5, 1.3, 1.5],
                                          dtype='f8')
        pr_time.attrs['unit'] = 's'
        players.dims.create_scale(pr_time, 'time')
        players.dims[1].attach_scale(pr_time)
        players.dims[1].label = 'time'

        tab0 = pr.create_group('table0')
        tab0.attrs['uid'] = tab0.name
        entities = tab0.create_dataset('entities', shape=(3,),
                                       data=['{}/ball0'.format(tab0.name),
                                             '{}/ball1'.format(tab0.name),
                                             '{}/ball2'.format(tab0.name)],
                                       dtype=VLENSTR)
        for entity in entities:
            grp = tab0.create_group(entity.rpartition('/')[-1])
            grp.attrs['uid'] = grp.name
        tab0_map = mgrp['uniform'].create_dataset('table0',
                                                  data=[entity
                                                        for entity in entities],
                                                  dtype=VLENSTR)
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] = tab0.ref
        tab0_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1,), dtype=OBJECTREF)
        map_ref[0] = tab0_map.ref
        tab0.attrs['map'] = map_ref

        tab0_data = dgrp['uniform'].create_group('table0')
        xdata = np.arange(1, 16, 1.0).reshape(3,5)                      
        x = tab0_data.create_dataset('x', data=xdata, dtype='f8')
        x.attrs['field'] = 'x'
        x.attrs['unit'] = 'm'
        x.attrs['tstart'] = 0.0
        x.attrs['tend'] = 1.0 * xdata.shape[1]
        x.attrs['endpoint'] = 1
        x.dims.create_scale(tab0_map, 'source')
        x.dims[0].attach_scale(tab0_map)
        x.dims[0].label = 'source'

        tab0_map = mgrp['event'].create_dataset('table0', shape=(3,),
                                                  dtype=[('source', VLENSTR), ('data', OBJECTREF)])
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] = tab0.ref
        tab0_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1+len(tab0.attrs['map']),), dtype=OBJECTREF)
        map_ref[-1] = tab0_map.ref
        map_ref[:-1] = tab0.attrs['map']
        tab0.attrs['map'] = map_ref

        tab0_data = dgrp['event'].create_group('table0')
        hit = tab0_data.create_group('hit')
        b0_hit = hit.create_dataset('ball0', data=[0.7, 0.8, 1.4], dtype='f8')
        b0_hit.attrs['field'] = 'hit'
        b0_hit.attrs['unit'] = 's'
        b0_hit.attrs['source'] = tab0_map.ref
        tab0_map[0] = (entities[0], b0_hit.ref)
        b1_hit = hit.create_dataset('ball1', data=[0.7, 0.8, 1.4], dtype='f8')
        b1_hit.attrs['field'] = 'hit'
        b1_hit.attrs['unit'] = 's'
        b1_hit.attrs['source'] = tab0_map.ref
        tab0_map[1] = (entities[1], b1_hit.ref)
        b2_hit = hit.create_dataset('ball2', data=[0.7, 0.8, 1.4], dtype='f8')
        b2_hit.attrs['field'] = 'hit'
        b2_hit.attrs['unit'] = 's'
        b2_hit.attrs['source'] = tab0_map.ref
        tab0_map[2] = (entities[2], b2_hit.ref)

        tab1 = pr.create_group('table1')
        tab1.attrs['uid'] = tab1.name
        entities = tab1.create_dataset('entities', shape=(3,),
                                       data=['{}/ball0'.format(tab1.name),
                                             '{}/ball1'.format(tab1.name),
                                             '{}/ball2'.format(tab1.name)],
                                       dtype=VLENSTR)
        for entity in entities:
            grp = tab1.create_group(entity.rpartition('/')[-1])
            grp.attrs['uid'] = grp.name

        tab1_map = mgrp['uniform'].create_dataset('table1',
                                                  data=[entity for entity in entities],
                                                  dtype=VLENSTR)
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] = tab1.ref
        tab1_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1,), dtype=OBJECTREF)
        map_ref[0] = tab1_map.ref
        tab1.attrs['map'] = map_ref

        tab1_data = dgrp['uniform'].create_group('table1')
        xdata = np.arange(1, 16, 1.0).reshape(3,5)                      
        x = tab1_data.create_dataset('x', data=xdata, dtype='f8')
        x.attrs['field'] = 'x'
        x.attrs['unit'] = 'm'
        x.attrs['tstart'] = 0.0
        x.attrs['tend'] = 1.0 * xdata.shape[1]
        x.attrs['endpoint'] = 1
        x.dims.create_scale(tab1_map, 'source')
        x.dims[0].attach_scale(tab1_map)
        x.dims[0].label = 'source'

        tab1_map = mgrp['event'].create_dataset('table1', shape=(3,),
                                                  dtype=[('source', VLENSTR),
                                                         ('data', OBJECTREF)])
        # map -> model
        model_ref = np.empty((1,), dtype=OBJECTREF)
        model_ref[0] = tab1.ref
        tab1_map.attrs['model'] = model_ref
        # model -> map
        map_ref = np.empty((1+len(tab1.attrs['map']),), dtype=OBJECTREF)
        map_ref[-1] = tab1_map.ref
        map_ref[:-1] = tab1.attrs['map']
        tab1.attrs['map'] = map_ref

        tab1_data = dgrp['event'].create_group('table1')
        hit = tab1_data.create_group('hit')
        b0_hit = hit.create_dataset('ball0', data=[0.7, 0.8, 1.4], dtype='f8')
        b0_hit.attrs['field'] = 'hit'
        b0_hit.attrs['unit'] = 's'
        b0_hit.attrs['source'] = tab1_map.ref
        tab1_map[0] = (entities[0], b0_hit.ref)
        b1_hit = hit.create_dataset('ball1', data=[0.7, 0.8, 1.4], dtype='f8')
        b1_hit.attrs['field'] = 'hit'
        b1_hit.attrs['unit'] = 's'
        b1_hit.attrs['source'] = tab1_map.ref
        tab1_map[1] = (entities[1], b1_hit.ref)
        b2_hit = hit.create_dataset('ball2', data=[0.7, 0.8, 1.4], dtype='f8')
        b2_hit.attrs['field'] = 'hit'
        b2_hit.attrs['unit'] = 's'
        b2_hit.attrs['source'] = tab1_map.ref
        tab1_map[2] = (entities[2], b2_hit.ref)
    
if __name__ == '__main__':
    create_example()
    print 'Finished'
    
# 
# poolroom.py ends here
