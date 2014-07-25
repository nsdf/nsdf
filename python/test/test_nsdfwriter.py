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

uid__ = 0
def getuid():
    """Increment the global uid tracker and return the value.

    Returns:
        str representation of the uid integer.
    """
    global uid__
    uid__ += 1
    return str(uid__)


def create_ob_model_tree():
        """This creates a model tree of the structure:

        /model
        |
        |__Granule
        |       |
        |       |__granule_0
        |       |       |__gc_0
        |       |       |__...
        |       |       |__gc_19
         ... ... ...
        |       |
        |       |__granule_9
        |               |__gc_0
        |               |__...
        |               |__gc_19 
        |__Mitral
        |       |
        |       |__mitral_0
        |       |       |__mc_0
        |       |       |__...
        |       |       |__mc_14
         ... ... ...
        |       |
        |       |__mitral_9
        |               |__mc_0
        |               |__...
        |               |__mc_19
       

        """
        uid = 0
        model_tree = nsdf.ModelComponent('model', uid=getuid())
        granule = nsdf.ModelComponent('Granule', uid=getuid(),
                                            parent=model_tree)
        mitral = nsdf.ModelComponent('Mitral', uid=getuid(),
                                           parent=model_tree)
        granule_cells = [nsdf.ModelComponent('granule_{}'.format(ii),
                                                 uid=getuid(),
                                                 parent=granule)
                                                 for ii in range(10)]
        mitral_cells = [nsdf.ModelComponent('mitral_{}'.format(ii),
                                                   uid=getuid(),
                                                   parent=mitral)
                                                 for ii in range(10)]
        for cell in granule_cells:
            cell.add_children([nsdf.ModelComponent('gc_{}'.format(ii),
                                                uid=getuid())
                               for ii in range(20)])
        for cell in mitral_cells:
            cell.add_children([nsdf.ModelComponent('mc_{}'.format(ii),
                                                    uid=getuid())
                               for ii in range(15)])
        return {'model_tree': model_tree,
                'granule_population': granule,
                'mitral_population': mitral,
                'granule_cells': granule_cells,
                'mitral_cells': mitral_cells}

    
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
        writer = nsdf.NSDFWriter(self.filepath)
        ds = writer.add_uniform_ds(self.popname,
                              self.granule_somata)
        self.datadict = {}
        self.dlen = 5
        for uid in self.granule_somata:
            self.datadict[uid] = np.random.uniform(-65, -55, size=self.dlen)
        self.dt = 1e-4
        self.name = 'Vm'
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.tstart = 0.0
        data = writer.add_uniform_data(self.name, ds, self.datadict,
                                       field=self.field, unit=self.unit,
                                       tstart=self.tstart, dt=self.dt,
                                       tunit=self.tunit)
        
                
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
            data = fd['/data'][nsdf.UNIFORM][self.popname][self.field]
            for row, source in zip(data, data.dims[0]['source']):
                nptest.assert_allclose(np.asarray(row), self.datadict[source])
            self.assertEqual(data.attrs['field'], self.field)
            self.assertEqual(data.attrs['unit'], self.unit)
            self.assertAlmostEqual(data.attrs['dt'], self.dt)
            self.assertAlmostEqual(data.attrs['tstart'], self.tstart)
        os.remove(self.filepath)

    def test_append_uniform_data(self):
        """Try appending data to existing uniformly sampled dataset"""
        # start over for appending data
        writer = nsdf.NSDFWriter(self.filepath)
        ds = writer.mapping['uniform'][self.popname]
        for uid in self.granule_somata:            
            self.datadict[uid] = np.random.uniform(-65, -55, size=self.dlen)
        data = writer.add_uniform_data(self.name, ds, self.datadict)
        del writer
        with h5.File(self.filepath, 'r') as fd:
            data = fd['data'][nsdf.UNIFORM][self.popname][self.name]
            for row, source in zip(data, data.dims[0]['source']):
                nptest.assert_allclose(row[-self.dlen:], self.datadict[source])
        os.remove(self.filepath)
        
    
class TestNSDFWriterNonuniform1D(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in 1D arrays"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = 'test_nsdfwriter_nonuniform_1d.h5'
        writer = nsdf.NSDFWriter(self.filepath,
                                 dialect=nsdf.dialect.ONED)
        writer.set_title(self.id())
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        ds = writer.add_nonuniform_ds(self.popname, mitral_somata)
        self.dlen = 1000
        self.src_name_dict = {}
        self.src_data_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen))
            self.src_data_dict[uid] = (data, times)
            self.src_name_dict[uid] = str('vm_{}'.format(ii))
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.varname = 'Vm'
        dd = writer.add_nonuniform_1d(self.varname,
                                           ds,self.src_name_dict,
                                           self.src_data_dict,
                                           field=self.field,
                                           unit=self.unit,
                                           tunit=self.tunit)

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
                    self.popname, self.varname)
                source_ds = fd[source_ds_path]
            except KeyError:
                self.fail('{} not created.'.format(source_ds_path))
            self.assertTrue(nsdf.match_datasets(source_ds['source'],
                                                self.src_data_dict.keys()))
        os.remove(self.filepath)
        
    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.varname)            
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                nptest.assert_allclose(np.asarray(self.src_data_dict[srcuid][0]),
                                       np.asarray(dataset))
                self.assertEqual(dataset.attrs['unit'], self.unit)
                self.assertEqual(dataset.attrs['field'], self.field)
        os.remove(self.filepath)

    def test_ts(self):
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.varname)
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                ts = dataset.dims[0]['time']
                nptest.assert_allclose(np.asarray(self.src_data_dict[srcuid][1]),
                                       np.asarray(ts))
                self.assertEqual(ts.attrs['unit'], self.tunit)
        os.remove(self.filepath)

                
class TestNSDFWriterNonuniformVlen(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in 2D ragged
    arrays"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath,
                                      dialect=nsdf.dialect.VLEN)
        writer.set_title(self.id())
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        ds = writer.add_nonuniform_ds(self.popname, mitral_somata)
        self.dlen = 1000
        self.src_data_dict = {}
        self.src_name_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen))
            self.src_data_dict[uid] = (data, times)
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.varname = 'Vm'
        dd = writer.add_nonuniform_vlen(self.varname, ds,
                                             self.src_data_dict,
                                             field=self.field,
                                             unit=self.unit,
                                             tunit=self.tunit)

    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            source_ds_name = '/map/{}/{}'.format(nsdf.NONUNIFORM,
                                                 self.popname,
                                                 self.varname)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.src_data_dict.keys()))            
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
                nptest.assert_allclose(self.src_data_dict[srcuid][0],
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
                nptest.assert_allclose(self.src_data_dict[srcuid][1],
                                       time_ds[ii])
        os.remove(self.filepath)


class TestNSDFWriterNonuniformRegular(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in homogeneous 2D
    arrays

    """
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath,
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
        self.src_data_dict = {}
        self.src_name_dict = {}
        self.times = np.random.uniform(0, 1, size=self.dlen)
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            self.src_data_dict[uid] = data
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.varname = 'Vm'
        dd = writer.add_nonuniform_regular(self.varname, ds,
                                             self.src_data_dict,
                                             self.times,
                                             field=self.field,
                                             unit=self.unit,
                                             tunit=self.tunit)        

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
                                                 self.varname)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.src_data_dict.keys()))
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
                nptest.assert_allclose(self.src_data_dict[srcuid],
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
            time_ds = dataset.dims[1]['time']
            self.assertEqual(time_ds.attrs['unit'], self.tunit)
            self.assertEqual(time_ds.shape, self.times.shape)
            nptest.assert_allclose(self.times, time_ds)
        os.remove(self.filepath)

        
class TestNSDFWriterEvent1D(unittest.TestCase):
    def setUp(self):
        """Create a poisson spike train for each cell in mitral population and
        save the data as 1D event data"""
        self.mdict = create_ob_model_tree()
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath,
                                      dialect=nsdf.dialect.ONED)
        writer.set_title(self.id())
        self.sources = [cell.uid for cell in self.mdict['mitral_cells']]
        self.popname = 'pop1'
        ds = writer.add_event_ds(self.popname, self.sources)
        self.src_data_dict = {}
        self.src_name_dict = {}
        rate = 100.0
        dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=dlen[ii]))
            self.src_data_dict[uid] = data
            # this is not required to be cell.name, any valid hdf5
            # name will do
            self.src_name_dict[uid] = cell.name    
        self.field = 'spike'
        self.unit = 's'
        self.varname = 'spike'
        dd = writer.add_event_1d(self.varname, ds, self.src_name_dict,
                                 self.src_data_dict,
                                 field=self.field,
                                 unit=self.unit)

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
                nptest.assert_allclose(np.asarray(self.src_data_dict[srcuid]),
                                       np.asarray(dataset))
                self.assertEqual(dataset.attrs['unit'], self.unit)
                self.assertEqual(dataset.attrs['field'], self.field)
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
        self.writer = nsdf.NSDFWriter(self.filepath,
                                      dialect=nsdf.dialect.VLEN)
        self.writer.set_title(self.id())
        self.sources = [cell.uid for cell in self.mdict['mitral_cells']]
        self.popname = 'pop1'
        ds = self.writer.add_event_ds(self.popname, self.sources)
        self.src_data_dict = {}
        self.src_name_dict = {}
        rate = 100.0
        dlen = np.random.poisson(lam=rate, size=len(self.sources))
        for ii, cell in enumerate(self.mdict['mitral_cells']):
            uid = cell.uid
            data = np.cumsum(np.random.exponential(scale=1.0/rate,
                                                   size=dlen[ii]))
            self.src_data_dict[uid] = data
            # this is not required to be cell.name, any valid hdf5
            # name will do
            self.src_name_dict[uid] = cell.name
        self.field = 'spike'
        self.unit = 's'
        self.varname = 'spike'
        dd = self.writer.add_event_vlen(self.varname, ds,
                                      self.src_data_dict,
                                      field=self.field,
                                      unit=self.unit)
        del self.writer
        
    def test_source_ds(self):
        with h5.File(self.filepath, 'r') as fd:
            source_ds_name = '/map/{}/{}'.format(nsdf.EVENT,
                                                 self.popname,
                                                 self.varname)
            source_ds = fd[source_ds_name]            
            self.assertTrue(nsdf.match_datasets(source_ds,
                                                self.src_data_dict.keys()))
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
                nptest.assert_allclose(self.src_data_dict[srcuid],
                                       dataset[ii])
        os.remove(self.filepath)


class TestNSDFWriterModelTree(unittest.TestCase):
    """Test the structure of model tree saved in `/model/modeltree` of the
    NSDF file.
    
    The goups in the model tree should get linked to source dimension
    scales in `/map`

    """
    def setUp(self):
        self.filepath = '{}.h5'.format(self.id())
        writer = nsdf.NSDFWriter(self.filepath,
                                 dialect=nsdf.dialect.ONED)

    def 

        
def main():
    unittest.main()

import subprocess

if __name__ == '__main__':
    main()


# 
# test_nsdfwriter.py ends here
