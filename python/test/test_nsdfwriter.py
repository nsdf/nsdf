# test_nsdfwriter.py --- 
# 
# Filename: test_nsdfwriter.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Jul 21 15:00:04 2014 (+0530)
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
"""Tests for the NSDFWriter class.

Hint:

If running this script throws the exception:

ValueError: Unable to create group (Name already exists)

try removing all hdf5 files from current working directory. These are
possibly files left from older tests which failed.

"""

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

    
class TestNSDFWriterUniform(unittest.TestCase):
    """Unit tests for check if adding data sources is working properly"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        self.granule_somata = []
        self.popname = 'pop0'
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    self.granule_somata.append(comp.uid)
        writer = nsdf.NSDFWriter(self.filepath, mode='w')
        source_ds = writer.add_uniform_ds(self.popname,
                              self.granule_somata)
        self.data_object = nsdf.UniformData('Vm', unit='mV', field='Vm')
        self.dlen = 5
        for uid in self.granule_somata:
            self.data_object.put_data(uid, np.random.uniform(-65, -55,
                                                             size=self.dlen))
        self.data_object.set_dt(1e-4, 's')
        self.tstart = 0.0
        data = writer.add_uniform_data(source_ds, self.data_object,
                                       tstart=self.tstart)        
                
    def test_add_uniform_ds(self):
        """Add the soma (gc_0) all the granule cells in olfactory bulb model
        as data sources for uniformly sampled data.

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                uniform_group = fd['map']['uniform']
            except KeyError:
                self.fail('/map/uniform group does not exist after'
                          ' adding uniform data sources')
            try:
                uniform_ds = fd['/map/uniform/pop0']
            except KeyError:
                self.fail('pop0 not created.')
            self.assertTrue(nsdf.match_datasets(uniform_ds, self.granule_somata))
        os.remove(self.filepath)

    def test_create_uniform_data(self):
        """Check that the uniform data was created alright for the first
        time."""
        with h5.File(self.filepath, 'r') as fd:
            uniform_container = fd['/data'][nsdf.UNIFORM]
            data = uniform_container[self.popname][self.data_object.field]
            for row, source in zip(data, data.dims[0]['source']):
                nptest.assert_allclose(np.asarray(row),
                                       self.data_object.get_data(source))
            self.assertEqual(data.attrs['field'], self.data_object.field)
            self.assertEqual(data.attrs['unit'], self.data_object.unit)
            self.assertAlmostEqual(data.attrs['dt'], self.data_object.dt)
            self.assertAlmostEqual(data.attrs['tstart'], self.tstart)
        os.remove(self.filepath)

    def test_append_data(self):
        """Try appending data to existing uniformly sampled dataset"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath, mode='a')
        ds = writer.mapping['uniform'][self.popname]
        for uid in self.granule_somata:            
            self.data_object.put_data(uid, np.random.uniform(-65, -55,
                                                             size=self.dlen))
        data = writer.add_uniform_data(ds, self.data_object)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            uniform_container = fd['/data'][nsdf.UNIFORM]
            data = uniform_container[self.popname][self.data_object.name]
            for row, source in zip(data, data.dims[0]['source']):
                nptest.assert_allclose(row[-self.dlen:], self.data_object.get_data(source))
        os.remove(self.filepath)
        
    
class TestNSDFWriterNonuniform1D(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in 1D arrays"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                 dialect=nsdf.dialect.ONED)
        writer.set_title(self.id())
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        self.data_object = nsdf.NonuniformData('Vm', unit='mV', field='Vm', tunit='ms')
        ds = writer.add_nonuniform_ds_1d(self.popname, self.data_object.name,
                                         mitral_somata)
        self.dlen = 1000
        self.src_name_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen))
            self.data_object.put_data(uid, (data, times))
            self.src_name_dict[uid] = str('vm_{}'.format(ii))
        dd = writer.add_nonuniform_1d(ds, self.data_object,
                                      self.src_name_dict)

    def test_source_ds_group(self):
        """Verify that the group for containing source-data mapping dataset
        has been created.

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                nonuniform_ds = fd['/map'][nsdf.NONUNIFORM][self.popname]
            except KeyError:
                self.fail('{} not created.'.format(self.popname))
            self.assertIsInstance(nonuniform_ds, h5.Group)
        os.remove(self.filepath)

    def test_source_ds(self):
        """Add the soma (gc_0) all the granule cells in olfactory bulb model
        as data sources for nonuniformly sampled data.

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                source_ds_path = '/map/{}/{}/{}'.format(
                    nsdf.NONUNIFORM,
                    self.popname, self.data_object.name)
                source_ds = fd[source_ds_path]
            except KeyError:
                self.fail('{} not created.'.format(source_ds_path))
            self.assertTrue(nsdf.match_datasets(source_ds['source'],
                                                self.data_object.get_sources()))
        os.remove(self.filepath)
        
    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.data_object.name)            
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                nptest.assert_allclose(np.asarray(self.data_object.get_data(srcuid)[0]),
                                       np.asarray(dataset))
                self.assertEqual(dataset.attrs['unit'], self.data_object.unit)
                self.assertEqual(dataset.attrs['field'], self.data_object.field)
        os.remove(self.filepath)

    def test_ts(self):
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.data_object.name)
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                ts = dataset.dims[0]['time']
                nptest.assert_allclose(np.asarray(self.data_object.get_data(srcuid)[1]),
                                       np.asarray(ts))
                self.assertEqual(ts.attrs['unit'], self.data_object.tunit)
        os.remove(self.filepath)

    def test_append_data(self):
        """Try appending data to existing nonuniform 1d datasets"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath, mode='a')
        ds = writer.mapping[nsdf.NONUNIFORM][self.popname][self.data_object.name]
        for uid in ds['source']:
            data = np.random.uniform(-65, -55, size=self.dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen))
            self.data_object.put_data(uid, (data, times))
        data = writer.add_nonuniform_1d(ds, self.data_object, self.src_name_dict)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            nucontainer = fd['/data'][nsdf.NONUNIFORM]
            data_grp = nucontainer[self.popname][self.data_object.name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                nptest.assert_allclose(self.data_object.get_data(srcuid)[0],
                                       dataset[-self.dlen:])
                ts = dataset.dims[0]['time']
                nptest.assert_allclose(self.data_object.get_data(srcuid)[1],
                                       ts[-self.dlen:])                
        os.remove(self.filepath)
        
                
class TestNSDFWriterNonuniformVlen(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in 2D ragged
    arrays"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                      dialect=nsdf.dialect.VLEN)
        writer.set_title(self.id())
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        self.dlen = np.random.randint(10, 100, size=len(mitral_somata))
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.varname = 'Vm'
        ds = writer.add_nonuniform_ds(self.popname, mitral_somata)
        # FIXME: vlen does not support float64
        self.data_object = nsdf.NonuniformData(self.varname,
                                               unit=self.unit,
                                               field=self.field,
                                               tunit=self.tunit,
                                               dtype=np.float32) 
        self.src_name_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen[ii])
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen[ii]))
            self.data_object.put_data(uid, (data, times))
        dd = writer.add_nonuniform_vlen(ds, self.data_object)

    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            source_ds_name = '/map/{}/{}'.format(nsdf.NONUNIFORM,
                                                 self.popname,
                                                 self.varname)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.data_object.get_sources()))
        os.remove(self.filepath)

    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            dataset_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                                   self.popname,
                                                   self.varname)            
            dataset = fd[dataset_name]
            self.assertIsInstance(dataset, h5.Dataset)
            src_ds_name = '/map/{}/{}'.format(nsdf.NONUNIFORM,
                                              self.popname)
            src_ds = fd[src_ds_name]            
            self.assertIsInstance(src_ds, h5.Dataset)
            attached_src_ds = dataset.dims[0]['source']          
            self.assertEqual(src_ds, attached_src_ds)
            self.assertEqual(dataset.attrs['unit'], self.unit)
            self.assertEqual(dataset.attrs['field'], self.field)    
            for ii in range(src_ds.len()):
                srcuid = src_ds[ii]                
                nptest.assert_allclose(self.data_object.get_data(srcuid)[0],
                                       dataset[ii])
        os.remove(self.filepath)

    def test_ts(self):
        with h5.File(self.filepath, 'r') as fd:
            dataset_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.varname)
            dataset = fd[dataset_name]
            self.assertIsInstance(dataset, h5.Dataset)            
            src_ds = dataset.dims[0]['source']
            time_ds = dataset.dims[0]['time']
            self.assertEqual(time_ds.attrs['unit'], self.tunit)
            self.assertEqual(time_ds.shape, dataset.shape)
            for ii in range(src_ds.len()):
                srcuid = src_ds[ii]                
                nptest.assert_allclose(self.data_object.get_data(srcuid)[1],
                                       time_ds[ii])
        os.remove(self.filepath)

    def test_append_data(self):
        """Try appending data to existing nonuniformly sampled vlen dataset"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath, mode='a',
                                 dialect=nsdf.dialect.VLEN)
        ds = writer.mapping[nsdf.NONUNIFORM][self.popname]
        dlen = np.random.randint(10, 100, size=ds.shape[0])
        for iii, uid in enumerate(ds):
            data = np.random.uniform(-65, -55, size=dlen[iii])
            times = np.cumsum(np.random.exponential(scale=0.01,
                                                    size=dlen[iii]))
            self.data_object.put_data(uid, (data, times))
        data = writer.add_nonuniform_vlen(ds, self.data_object)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            ds = fd['map'][nsdf.NONUNIFORM][self.popname]
            dataset = fd['/data'][nsdf.NONUNIFORM][self.popname][self.varname]
            ts = dataset.dims[0]['time']
            for iii, source in enumerate(ds):
                data, times = self.data_object.get_data(source)
                nptest.assert_allclose(data,
                                       dataset[iii][-len(data):])
                nptest.assert_allclose(times,
                                       ts[iii][-len(data):])
        os.remove(self.filepath)


class TestNSDFWriterNonuniformRegular(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in homogeneous 2D
    arrays

    """
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                      dialect=nsdf.dialect.NUREGULAR)
        writer.set_title(self.id())
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        ds = writer.add_nonuniform_ds(self.popname, mitral_somata)
        self.dlen = 1000
        self.data_object = nsdf.NonuniformRegularData(name='Vm',
                                                      unit='mV', tunit='ms')
        self.data_object.set_times(np.random.uniform(0, 1, size=self.dlen))
        self.src_name_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            self.data_object.put_data(uid, data)
        dd = writer.add_nonuniform_regular(ds,
                                           self.data_object)    

    def test_adding_ds_creates_group(self):
        """Check that adding nonuniform data sources creates the 'nonuniform'
        group under '/map'

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                nonuniform_group = fd['map']['nonuniform']
            except KeyError:
                self.fail('/map/nonuniform group does not exist after'
                          ' adding nonuniform data sources')
        os.remove(self.filepath)
                    
    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            source_ds_name = '/map/{}/{}'.format(nsdf.NONUNIFORM,
                                                 self.popname,
                                                 self.data_object.name)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.data_object.get_sources()))
        os.remove(self.filepath)

    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            dataset_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                                   self.popname,
                                                   self.data_object.name)
            dataset = fd[dataset_name]
            self.assertIsInstance(dataset, h5.Dataset)
            src_ds_name = '/map/{}/{}'.format(nsdf.NONUNIFORM,
                                              self.popname)
            src_ds = fd[src_ds_name]            
            self.assertIsInstance(src_ds, h5.Dataset)
            attached_src_ds = dataset.dims[0]['source']          
            self.assertEqual(src_ds, attached_src_ds)
            self.assertEqual(dataset.attrs['unit'], self.data_object.unit)
            self.assertEqual(dataset.attrs['field'], self.data_object.field)    
            for ii in range(src_ds.len()):
                srcuid = src_ds[ii]                
                nptest.assert_allclose(self.data_object.get_data(srcuid),
                                       dataset[ii])
        os.remove(self.filepath)

    def test_ts(self):
        with h5.File(self.filepath, 'r') as fd:
            dataset_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.data_object.name)
            dataset = fd[dataset_name]
            self.assertIsInstance(dataset, h5.Dataset)            
            time_ds = dataset.dims[1]['time']
            self.assertEqual(time_ds.attrs['unit'], self.data_object.tunit)
            self.assertEqual(time_ds.shape, self.data_object.get_times().shape)
            nptest.assert_allclose(self.data_object.get_times(), time_ds)
        os.remove(self.filepath)
        
        
class TestNSDFWriterEvent1D(unittest.TestCase):
    def setUp(self):
        """Create a poisson spike train for each cell in mitral population and
        save the data as 1D event data"""
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                      dialect=nsdf.dialect.ONED)
        writer.set_title(self.id())
        self.sources = [cell.uid for cell in self.mdict['mitral_cells']]
        self.popname = 'pop1'
        self.field = 'spike'
        self.unit = 's'
        self.varname = 'spike'
        ds = writer.add_event_ds_1d(self.popname, self.varname, self.sources)
        self.data_object = nsdf.EventData(self.varname,
                                          unit=self.unit,
                                          field=self.field)
        self.src_name_dict = {}
        rate = 100.0
        self.dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=self.dlen[ii]))
            self.data_object.put_data(uid, data)
            # this is not required to be cell.name, any valid hdf5
            # name will do
            self.src_name_dict[uid] = cell.name    
        dd = writer.add_event_1d(ds, self.data_object, self.src_name_dict)

    def test_adding_ds_event_creates_event_group(self):
        """Check that adding nonuniform data sources creates the '/nonuniform'
        group under '/map'

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                nonuniform_group = fd['map']['event']
            except KeyError:
                self.fail('/map/event group does not exist after'
                          ' adding event data sources')
        os.remove(self.filepath)

    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            try:
                source_ds_path = 'map/{}/{}/{}'.format(nsdf.EVENT,
                                                         self.popname,
                                                         self.varname)
                source_ds = fd[source_ds_path]
            except KeyError:
                self.fail('{} does not exist after'
                          ' adding event data sources'.source_ds_path)
            self.assertTrue(nsdf.match_datasets(source_ds['source'],
                                                self.sources))
        os.remove(self.filepath)                                       
                                       
    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.EVENT,
                                               self.popname,
                                               self.varname)            
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                nptest.assert_allclose(self.data_object.get_data(srcuid),
                                       dataset)
                self.assertEqual(dataset.attrs['unit'], self.unit)
                self.assertEqual(dataset.attrs['field'], self.field)
        os.remove(self.filepath)

    def test_append_data(self):
        """Try appending data to existing 1D event dataset"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath, mode='a')
        ds = writer.mapping[nsdf.EVENT][self.popname][self.data_object.name]
        rate = 100.0
        new_dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=new_dlen[ii]))
            self.data_object.put_data(uid, data)
        writer.add_event_1d(ds, self.data_object, self.src_name_dict)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            eventcontainer = fd['/data'][nsdf.EVENT]
            data_grp = eventcontainer[self.popname][self.data_object.name]
            for ii, cell in enumerate(self.mdict['mitral_cells']):
                uid = cell.uid            
                dataset = data_grp[cell.name]
                nptest.assert_allclose(self.data_object.get_data(uid),
                                       dataset[self.dlen[ii]:])
        os.remove(self.filepath)


class TestNSDFWriterEventVlen(unittest.TestCase):
    """Test case for writing event data in 2D ragged arrays

    """
    def setUp(self):
        """Create a poisson spike train for each cell in mitral population and
        save the data as 1D event data

        """
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        self.writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                      dialect=nsdf.dialect.VLEN)
        self.writer.set_title(self.id())
        self.sources = [cell.uid for cell in self.mdict['mitral_cells']]
        self.popname = 'pop1'
        self.field = 'spike'
        self.unit = 's'
        self.varname = 'spike'
        ds = self.writer.add_event_ds(self.popname, self.sources)
        # FIXME: h5py does not support vlen data with float64 type
        # entries
        self.data_object = nsdf.EventData(self.varname,
                                          unit=self.unit,
                                          field=self.field,
                                          dtype=np.float32)
        self.src_name_dict = {}
        rate = 100.0
        dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=dlen[ii]))
            self.data_object.put_data(uid, data)
            # this is not required to be cell.name, any valid hdf5
            # name will do
            self.src_name_dict[uid] = cell.name
        dd = self.writer.add_event_vlen(ds,
                                      self.data_object)
        del self.writer
        
    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            source_ds_name = '/map/{}/{}'.format(nsdf.EVENT,
                                                 self.popname,
                                                 self.varname)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.data_object.get_sources()))
        os.remove(self.filepath)          

    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            dataset_name = '/data/{}/{}/{}'.format(nsdf.EVENT,
                                                   self.popname,
                                                   self.varname)            
            dataset = fd[dataset_name]
            self.assertIsInstance(dataset, h5.Dataset)
            src_ds_name = '/map/{}/{}'.format(nsdf.EVENT,
                                              self.popname)
            src_ds = fd[src_ds_name]            
            self.assertIsInstance(src_ds, h5.Dataset)
            attached_src_ds = dataset.dims[0]['source']          
            self.assertEqual(src_ds, attached_src_ds)
            self.assertEqual(dataset.attrs['unit'], self.unit)
            self.assertEqual(dataset.attrs['field'], self.field)    
            for ii in range(src_ds.len()):
                srcuid = src_ds[ii]                
                nptest.assert_allclose(self.data_object.get_data(srcuid),
                                       dataset[ii])
        os.remove(self.filepath)


class TestNSDFWriterEventNanPadded(unittest.TestCase):
    """Test the case of writing event data with NaN padding"""
    def setUp(self):
        """Create a poisson spike train for each cell in mitral population and
        save the data as 1D event data"""
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                      dialect=nsdf.dialect.NANPADDED)
        writer.set_title(self.id())
        self.sources = [cell.uid for cell in self.mdict['mitral_cells']]
        self.popname = 'pop1'
        self.field = 'spike'
        self.unit = 's'
        self.varname = 'spike'
        ds = writer.add_event_ds(self.popname, self.sources)
        self.data_object = nsdf.EventData(self.varname,
                                          unit=self.unit,
                                          field=self.field)
        self.src_name_dict = {}
        rate = 100.0
        self.dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=self.dlen[ii]))
            self.data_object.put_data(uid, data)
            # this is not required to be cell.name, any valid hdf5
            # name will do
            self.src_name_dict[uid] = cell.name    
        dd = writer.add_event_nan(ds, self.data_object)

    def test_adding_ds_event_creates_event_group(self):
        """Check that adding event data sources creates the '/event' group
        under '/map'

        """
        with h5.File(self.filepath, 'r') as fd:
            try:
                nonuniform_group = fd['map']['event']
            except KeyError:
                self.fail('/map/event group does not exist after'
                          ' adding event data sources')
        os.remove(self.filepath)

    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            try:
                source_ds_path = 'map/{}/{}'.format(nsdf.EVENT,
                                                         self.popname)
                source_ds = fd[source_ds_path]
            except KeyError:
                self.fail('{} does not exist after'
                          ' adding event data sources'.source_ds_path)
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.sources))
        os.remove(self.filepath)                                       
                                       
    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            data_path = '/data/{}/{}/{}'.format(nsdf.EVENT,
                                               self.popname,
                                               self.varname)
            dataset = fd[data_path]            
            source_ds = dataset.dims[0]['source']
            for iii, srcuid in enumerate(source_ds):
                data = self.data_object.get_data(srcuid)
                nptest.assert_allclose(data,
                                       dataset[iii, :len(data)])
                nptest.assert_equal(dataset[iii, len(data):], np.nan)
            self.assertEqual(dataset.attrs['unit'], self.unit)
            self.assertEqual(dataset.attrs['field'], self.field)
        os.remove(self.filepath)

    def test_append_data(self):
        """Try appending data to existing NaN-padded event dataset"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath, mode='a',
                                 dialect=nsdf.dialect.NANPADDED)
        source_ds = writer.mapping[nsdf.EVENT][self.popname]
        rate = 100.0
        new_dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=new_dlen[ii]))
            self.data_object.put_data(uid, data)
        writer.add_event_nan(source_ds, self.data_object)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            dataset = fd['/data'][nsdf.EVENT][self.popname][self.varname]
            for ii, cell in enumerate(self.mdict['mitral_cells']):
                uid = cell.uid
                orig_data = self.data_object.get_data(uid)
                file_data = dataset[ii, self.dlen[ii]:self.dlen[ii]+new_dlen[ii]]
                nptest.assert_allclose(orig_data, file_data)
                nptest.assert_allclose(dataset[self.dlen[ii] +
                                               new_dlen[ii]:], np.nan)
        os.remove(self.filepath)


class TestNSDFWriterModelTree(unittest.TestCase):
    """Test the structure of model tree saved in `/model/modeltree` of the
    NSDF file.
    
    The goups in the model tree should get linked to source dimension
    scales in `/map`

    """
    def setUp(self):
        self.mdict = create_ob_model_tree()
        # self.mdict['model_tree'].print_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath, mode='w',
                                 dialect=nsdf.dialect.ONED)
        writer.add_modeltree(self.mdict['model_tree'])
        # print '######## Model Tree ################'
        # writer.modelroot.print_tree()
        # print '========================'
        self.granule_somata = []
        self.popname = 'pop0'
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    self.granule_somata.append(comp.uid)
        uds = writer.add_uniform_ds(self.popname,
                              self.granule_somata)
        self.data_object = nsdf.UniformData('Vm', unit='mV', field='Vm')
        self.dlen = 5
        for uid in self.granule_somata:
            self.data_object.put_data(uid, np.random.uniform(-65, -55,
                                                             size=self.dlen))
        self.data_object.set_dt(1e-4, 's')
        self.tstart = 0.0
        data = writer.add_uniform_data(uds, self.data_object,
                                       tstart=self.tstart)        
        
    def test_add_modeltree(self):
        """For each node in model tree see if the corresponding group
        has been created."""
        def nodes_match(node, hdfroot):
            try:
                grp = hdfroot[node.path[1:]]
            except KeyError:
                self.fail('{} does not exist in nsdf file'.format(node.path))
                
        with h5.File(self.filepath, 'r') as fd:
            hdfroot = fd['/model']
            self.mdict['model_tree'].visit(nodes_match, hdfroot)
        os.remove(self.filepath)

    def test_model_map_linking(self):
        """Check if each group in the model is linked to the source maps of
        which its children are members.

        """
        def check_child_in_map(name, obj):
            if not isinstance(obj, h5.Group):
                return
            fd = obj.file
            children = set([obj[chname].attrs['uid'] for chname in obj])
            try:
                for ref in obj.attrs['map']:
                    # For uniform datasets the source DS under map is a 1D dataset.
                    if fd[ref].dtype.fields is None:
                        map_ = set(fd[ref])
                    else:
                        # event and nonuniform data are stored in 1D
                        # datasets, the map tables will have two columns,
                        # `source` column storing the uid of the source
                        # component.
                        map_ = set(fd[ref]['source'])
                    # If this component refers to a map table, then
                    # one or more of its children must be members of
                    # the map table.
                    self.assertFalse(map_.intersection(children))
            except KeyError:
                pass

        with h5.File(self.filepath, 'r') as fd:
            fd['/model/modeltree/model'].visititems(check_child_in_map)            
        os.remove(self.filepath)
        
    def test_map_in_ds(self):
        """Check that the references in `map` attribute are part of the
        datasets under `/map` (i.e. they have paths starting with
        /map).

        """
        result = []
        def check_map_in_ds(node, obj):
            """Check if the path of all the map attribute entries start with
            '/map'"""
            try:
                for ref in obj.attrs['map']:
                    result.append(obj.file[ref].name.startswith('/map'))
            except KeyError:
                pass
            return None
        
        with h5.File(self.filepath, 'r') as fd:
            fd['/model/modeltree/model'].visititems(check_map_in_ds)
            self.assertTrue(len(result) > 0)
            self.assertNotIn(False, result)
        os.remove(self.filepath)

    def test_map_model_linking(self):
        """Check that every source uid entry in map is also under one of the
        references in the `model` attribute.

        """
        map_ds_list = []
        ds_collector = nsdf.node_finder(map_ds_list,
                                        lambda x: isinstance(x, h5.Dataset))
        model_uids = []
        with h5.File(self.filepath, 'r') as fd:
            fd['/map'].visititems(ds_collector)
            fd['/model/modeltree'].visititems(
                lambda name, obj: model_uids.append(obj.attrs['uid']))
            for source_ds in map_ds_list:
                source_refs = source_ds.attrs['model']
                model_uids = set(model_uids)
                if source_ds.dtype.fields is not None:
                    source_ds = np.asarray(source_ds['source'])
                source_uids = set(source_ds)
                self.assertEqual(source_uids, model_uids.intersection(source_uids))
        os.remove(self.filepath)
        
def main():
    unittest.main()

import subprocess

if __name__ == '__main__':
    main()


# 
# test_nsdfwriter.py ends here
