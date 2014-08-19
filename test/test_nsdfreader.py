# test_nsdfreader.py --- 
# 
# Filename: test_nsdfreader.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Sat Aug  9 15:26:14 2014 (+0530)
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
"""Test the reading of NSDF file in Python"""

import sys
from collections import defaultdict
import numpy as np
from numpy import testing as nptest
import h5py as h5
from datetime import datetime
import unittest
import os

sys.path.append('..')
import nsdf

from util import *

def create_test_data_file(filename, dialect):
    """Create a datafile at path `filename` using dialect `dialect`. 

    """
    mdict = create_ob_model_tree()
    uniform_data = nsdf.UniformData('Vm', unit='mV', field='Vm',
                                    dt=1e-2, tunit='ms')
    for cell in mdict['granule_cells']:
        uniform_data.put_data(cell.children['gc_0'].uid, np.random.uniform(-63, -57, 100))
        
    nonuniform_data = nsdf.NonuniformData('Im', unit='pA', field='Im')
    if dialect == nsdf.dialect.NUREGULAR:
        sizes = [150] * len(mdict['mitral_cells'])
    else:
        sizes = 150 + np.random.randint(-50, 50, len(mdict['mitral_cells']))
    for ii, cell in enumerate(mdict['mitral_cells']):
        nonuniform_data.put_data(cell.children['mc_0'].uid,
                                 (np.random.rand(sizes[ii]),
                                  np.cumsum(np.random.rand(sizes[ii]))))
    sizes = 200 + np.random.randint(-50, 50, len(mdict['cells']))
    event_data = nsdf.EventData('spike', unit='ms')
    for ii, cell in enumerate(mdict['cells']):
        times = np.cumsum(np.exponential(scale=0.01, size=sizes[ii]))
        event_data.put_data(cell.uid, times)
    writer = nsdf.NSDFWriter(filename, dialect=dialect, mode='w')
    writer.add_modeltree(mdict['model_tree'])
    uniform_ds = writer.add_uniform_ds('Vm', uniform_data.get_sources())
    writer.add_uniform_data(uniform_ds, uniform_data)
    
    if dialect == nsdf.dialect.ONED:
        nonuniform_ds = writer.add_nonuniform_ds_1d(
            'mitral', 'Vm',
            nonuniform_data.get_sources())
    else:
        nonuniform_ds = writer.add_nonuniform_ds('mitral',
                                                 nonuniform_data.get_sources())
    if (dialect == nsdf.dialect.ONED) or (dialect == nsdf.dialect.NUREGULAR):
        event_ds = writer.add_event_ds_1d('cells', 'spike',
                                          event_data.get_sources())
    else:
        event_ds = writer.add_event_ds('cells', event_data.get_sources())
    if dialect == nsdf.dialect.ONED:
        writer.add_nonuniform_1d(nonuniform_ds, nonuniform_data)
        writer.add_event_1d(event_ds, event_data)
    elif dialect == nsdf.dialect.NUREGULAR:
        writer.add_nonuniform_regular(nonuniform_ds, nonuniform_data)
        writer.add_event_1d(event_ds, event_data)
    elif dialect == nsdf.dialect.VLEN:
        writer.add_nonuniform_vlen(nonuniform_ds, nonuniform_data)
        writer.add_event_vlen(event_ds, event_data)
    elif dialect == nsdf.dialect.NANPADDED:
        writer.add_nonuniform_nan(nonuniform_ds, nonuniform_data)
        writer.add_event_nan(event_ds, event_data)
    else:
        raise Exception('unknown dialect: {}'.format(dialect))
    return {'uniform_data': uniform_data,
            'nonuniform_data': nonuniform_data,
            'event_data': event_data}
    



class TestNSDFReaderOneD(unittest.TestCase):
    """Check that file written in ONED dialect is read correctly"""
    def setUp(self):
        filename = '{}.h5'.format(self.id)
        self.data_dict = create_test_data_file(filename,
                                               nsdf.dialect.ONED)

    def test_get_uniform_data(self):
        raise NotImplementedError('Fix me')

    def test_get_uniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_ts(self):
        raise NotImplementedError('Fix me')

    def get_uniform_data(self):
        raise NotImplementedError('Fix me')

    def get_nonuniform_data(self):
        raise NotImplementedError('Fix me')

    def get_event_data(self):
        raise NotImplementedError('Fix me')


                                               

# 
# test_nsdfreader.py ends here
