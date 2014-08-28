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
import itertools as it
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
        
    if dialect == nsdf.dialect.NUREGULAR:
        size = 150
        nonuniform_data = nsdf.NonuniformRegularData('Im', unit='pA', field='Im', tunit='ms')
        nonuniform_data.set_times(np.cumsum(np.random.rand(size)))
        for ii, cell in enumerate(mdict['mitral_cells']):
            nonuniform_data.put_data(cell.children['mc_0'].uid,
                                     np.random.rand(size))
    else:
        nonuniform_data = nsdf.NonuniformData('Im', unit='pA', field='Im', tunit='ms', dtype=np.float32)
        sizes = 150 + np.random.randint(-50, 50, len(mdict['mitral_cells']))
        for ii, cell in enumerate(mdict['mitral_cells']):
            data = np.random.rand(sizes[ii])
            times = np.cumsum(np.random.rand(sizes[ii]))
            assert len(data) == len(times)
            nonuniform_data.put_data(cell.children['mc_0'].uid,
                                     (data, times))
    sizes = 200 + np.random.randint(-50, 50, len(mdict['cells']))
    event_data = nsdf.EventData('spike', unit='ms', dtype=np.float32)
    for ii, cell in enumerate(mdict['cells']):
        times = np.cumsum(np.random.exponential(scale=0.01, size=sizes[ii]))
        event_data.put_data(cell.uid, times)
    writer = nsdf.NSDFWriter(filename, dialect=dialect, mode='w')
    writer.add_modeltree(mdict['model_tree'])
    uniform_ds = writer.add_uniform_ds('granule', uniform_data.get_sources())
    writer.add_uniform_data(uniform_ds, uniform_data)
    
    if dialect == nsdf.dialect.ONED:
        nonuniform_ds = writer.add_nonuniform_ds_1d(
            'mitral', 'Im',
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
        self.filename = '{}.h5'.format(self.id())
        self.data_dict = create_test_data_file(self.filename,
                                               nsdf.dialect.ONED)

    def test_get_uniform_data(self):
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_uniform_data('granule', 'Vm')
        data = self.data_dict['uniform_data']
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        self.assertAlmostEqual(data.dt, file_data.dt)
        for src in data.get_sources():
            np.testing.assert_allclose(data.get_data(src),
                                       file_data.get_data(src))
        
    def test_get_uniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_data(self):
        data = self.data_dict['nonuniform_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_nonuniform_data('mitral', 'Im')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        for src in data.get_sources():
            var, times = data.get_data(src)
            fvar, ftimes = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)
            np.testing.assert_allclose(times, ftimes)
        
    def test_get_event_data(self):
        data = self.data_dict['event_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_event_data('cells', 'spike')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        for src in data.get_sources():
            var = data.get_data(src)
            fvar = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)


class TestNSDFReaderNAN(unittest.TestCase):
    """Check that file written in ONED dialect is read correctly"""
    def setUp(self):
        self.filename = '{}.h5'.format(self.id())
        self.data_dict = create_test_data_file(self.filename,
                                               nsdf.dialect.NANPADDED)

    def test_get_uniform_data(self):
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_uniform_data('granule', 'Vm')
        data = self.data_dict['uniform_data']
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        self.assertAlmostEqual(data.dt, file_data.dt)
        for src in data.get_sources():
            np.testing.assert_allclose(data.get_data(src),
                                       file_data.get_data(src))
        
    def test_get_uniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_data(self):
        data = self.data_dict['nonuniform_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_nonuniform_data('mitral', 'Im')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        for src in data.get_sources():
            var, times = data.get_data(src)
            fvar, ftimes = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)
            np.testing.assert_allclose(times, ftimes)
        
    def test_get_event_data(self):
        data = self.data_dict['event_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_event_data('cells', 'spike')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        for src in data.get_sources():
            var = data.get_data(src)
            fvar = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)

class TestNSDFReaderVLEN(unittest.TestCase):
    """Check that file written in ONED dialect is read correctly"""
    def setUp(self):
        self.filename = '{}.h5'.format(self.id())
        self.data_dict = create_test_data_file(self.filename,
                                               nsdf.dialect.VLEN)

    # def test_get_uniform_data(self):
    #     reader = nsdf.NSDFReader(self.filename)
    #     file_data = reader.get_uniform_data('granule', 'Vm')
    #     data = self.data_dict['uniform_data']
    #     self.assertEqual(set(file_data.get_sources()),
    #                      set(data.get_sources()))
    #     self.assertEqual(data.unit, file_data.unit)
    #     self.assertEqual(data.name, file_data.name)
    #     self.assertEqual(data.tunit, file_data.tunit)
    #     self.assertAlmostEqual(data.dt, file_data.dt)
    #     for src in data.get_sources():
    #         np.testing.assert_allclose(data.get_data(src),
    #                                    file_data.get_data(src))
        
    # def test_get_uniform_ts(self):
    #     raise NotImplementedError('Fix me')

    # def test_get_nonuniform_ts(self):
    #     raise NotImplementedError('Fix me')

    def test_get_nonuniform_data(self):
        data = self.data_dict['nonuniform_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_nonuniform_data('mitral', 'Im')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        for src in data.get_sources():
            var, times = data.get_data(src)
            fvar, ftimes = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)
            np.testing.assert_allclose(times, ftimes)
        
    def test_get_event_data(self):
        data = self.data_dict['event_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_event_data('cells', 'spike')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        for src in data.get_sources():
            var = data.get_data(src)
            fvar = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)

class TestNSDFReaderNUREGULAR(unittest.TestCase):
    """Check that file written in NUREGULAR dialect is read correctly"""
    def setUp(self):
        self.filename = '{}.h5'.format(self.id())
        self.data_dict = create_test_data_file(self.filename,
                                               nsdf.dialect.NUREGULAR)

    def test_get_uniform_data(self):
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_uniform_data('granule', 'Vm')
        data = self.data_dict['uniform_data']
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        self.assertAlmostEqual(data.dt, file_data.dt)
        for src in data.get_sources():
            ddata = data.get_data(src)
            fdata = file_data.get_data(src)
            np.testing.assert_allclose(ddata, fdata)
        
    def test_get_uniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_ts(self):
        raise NotImplementedError('Fix me')

    def test_get_nonuniform_data(self):
        data = self.data_dict['nonuniform_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_nonuniform_data('mitral', 'Im')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        self.assertEqual(data.tunit, file_data.tunit)
        times = data.get_times()
        ftimes = file_data.get_times()
        np.testing.assert_allclose(times, ftimes)
        for src in data.get_sources():
            var = data.get_data(src)
            fvar = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)
        
    def test_get_event_data(self):
        data = self.data_dict['event_data']
        reader = nsdf.NSDFReader(self.filename)
        file_data = reader.get_event_data('cells', 'spike')
        self.assertEqual(set(file_data.get_sources()),
                         set(data.get_sources()))
        self.assertEqual(data.unit, file_data.unit)
        self.assertEqual(data.name, file_data.name)
        for src in data.get_sources():
            var = data.get_data(src)
            fvar = file_data.get_data(src)
            np.testing.assert_allclose(var, fvar)
            
            
if __name__ == '__main__':
    unittest.main()

# 
# test_nsdfreader.py ends here
