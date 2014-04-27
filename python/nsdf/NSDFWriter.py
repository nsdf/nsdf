# NSDFWriter.py --- 
# 
# Filename: NSDFWriter.py
# Description: 
# Author: Subhasis Ray [email: {lastname} dot {firstname} at gmail dot com]
# Maintainer: 
# Created: Fri Apr 25 19:51:42 2014 (+0530)
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

import h5py as h5
import numpy as np


class NSDFWriter(object):
    """Writer of NSDF files."""
    def __init__(self, filename, prefer_vlen=False):
        self._fd = h5.File(filename, 'w')
        self.prefer_vlen = prefer_vlen
        self.data = self._fd.create_group('/data')
        self.model = self._fd.create_group('/model')
        self.map_ = self._fd.create_group('/map')
        self.uniform_data = self.data.create_group('uniform')
        self.nonuniform_data = self.data.create_group('nonuniform')
        self.event_data = self.data.create_group('event')
        self.uniform_map = self.map_.create_group('uniform')
        self.nonuniform_map = self.map_.create_group('nonuniform')
        self.event_map = self.map_.create_group('event')
        self.time_dim = self.map_.create_group('time') # dimension scales for time
        self.uniform_time_dim = self.time_dim.create_group('uniform')
        self.nonuniform_time_dim = self.time_dim.create_group('nonuniform')
        self.space_dim = self.map_.create_group('space') # dimension scales for space
        self.model_population = self.model.create_group('population')
        self.model_connectivity = self.model.create_group('connectivity')

    def __del__(self):
        self._fd.close()

    def add_uniform_dataset(self, population_name, dataset_name, datalist,
                            sourcelist=None, times=None,
                            t_start=0.0, t_end=None, endpoint=False,
                            unit=None,
                            t_unit=None):
        """Add a uniformly distributed dataset to the file. 

        Save uniformly sampled dataset in the NSDF file. This will
        create the dataset under
        /data/uniform/{population_name}/{dataset_name}, first creating
        the group {population_name} if not already present.  If
        `sourcelist` is specified, it will create a new dataset
        containing the entries in `sourcelist` under
        /model/population/{population_name} if required. It also
        creates a dimension scale /map/uniform/{population_name} and
        attaches this to the first dimension (rows) of the dataset. If
        `times` is specified, it will store this as a dimension scale
        /map/time/uniform/{population_name}/{dataset_name} creating
        the group {population_name} if required and will attach it to
        the second dimension (columns). If `t_end` is specified, in
        stead of explicitly storing the time dimension it will store
        `t_start` and `t_end` and `endpoint` as attributes of the
        dataset. `endpoint` should be True if t_end is the last
        sampling point (same meaning as numpy.linspace).

        Args:
            population_name: string name for the source
                population. A dataset of variable length strings is 
                created under /model/population and /map/uniform 
                unless a population of the same name already exists.
                /map/uniform is turned into a dimension scale and is 
                attached to the first (row) dimension of the dataset.
                If a population of the same name exists in either or 
                both locations, the size of the existing population 
                must match the number of rows in the dataset. 
                Otherwise a ValueError is raised.

            dataset_name: string specifying the name of the dataset.
        
            datalist: a 2D numpy array of doubles (64 bit float). 

            sourcelist: list of string specifying the source object
                identifiers. An object identifier can be any string.
                If None or unspecified, a population with name 
                `population_name` must already exist in 
                `/model/population` as well as `/map/uniform`.
                default: None

            times: float array of sampling times (optional). This is
                mutually exclusive with t_end.

            t_start: A float representing start time of sampling (optional) 

            t_end: A float representing end time of sampling (optional)

            endpoint: A bool specifying if `t_end` is to be taken as
                the last sampling point.

            unit: (optional) string specifying the unit of the
                quantity. If specified, this will be stored in the `UNIT`
                attribute of the dataset.

            t_unit: (optional) string specifying the unit of time in
                sampling time. If specified, this is stored in the
                label of the second dimension of the
                dataset. Moreover, if a dimension scale is created for
                sampling times, then that also gets this value in its
                UNIT attribute.

        Returns:
            None

        Raises:
            ValueError: sourcelist and dataset length do not match.
                or population of name `population_name` exists but the length does not match 
                or sourcelist is unspecified and no population of name `population_name` exists
                or sourcelist is unspecified and no dimension scale of name `population_name` exists
                or both `times` and `t_end` have been passed
                or dataset already exists

        """
        if sourcelist and (len(sourcelist) != len(datalist)):
            raise ValueError('number of sources must match rows in datalist')
        if times and (t_end is not None):
            raise ValueError('only one of `times` or `t_end` can be specified.')
        if times and (len(times) != datalist.shape[1]):
            raise ValueError('number of time points specified must match number of columns in datalist')        
        try:
            population = self.uniform_data[population_name]
        except KeyError:
            population = None
        try:
            if population and population[dataset_name]:
                raise ValueError('Dataset with name %s already exists')
        except KeyError:
            pass
        try:
            model = self.model_population[population_name]
            if len(model) != len(datalist):
                raise ValueError('size of existing population under %s does not match size of dataset.' %
                                 (self.model_population.path))
        except KeyError:
            if not sourcelist:
                raise ValueError('No source list specified and no existing population with name `%s`'
                                 % (population_name))
            model = None            
        try:
            source_dim = self.uniform_map[population_name]
        except KeyError:
            if not sourcelist:
                raise ValueError('No population specified and no existing dimension scale population with name `%s`'
                                 % (population_name))
            source_dim = None
        if population is None:
            population = self.uniform_data.create_group(population_name)
            
        dataset = population.create_dataset(dataset_name, data=datalist, dtype=np.float64)
        if unit is not None:
            dataset.attrs['UNIT'] = unit

        if model is None:
            model = self.model_population.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist])
        if source_dim is None:
            source_dim = self.uniform_map.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist])
            dataset.dims.create_scale(source_dim, 'source')
            dataset.dims[0].attach_scale(source_dim)
        if times:
            try:
                time_pop =  self.uniform_time_dim[population_name]
            except KeyError:
                time_pop = self.uniform_time_dim.create_group(population_name)
            time_dim = time_pop.create_dataset(dataset_name, data=times, dtype=np.float64)
            dataset.dims.create_scale(time_dim, 'time')
            dataset.dims[1].attach_scale(time_dim)
            if t_unit is not None:
                time_dim.attrs['UNIT'] = t_unit
        elif t_end is not None:
            dataset.attrs['t_start'] = t_start
            dataset.attrs['t_end'] = t_end
            dataset.attrs['endpoint'] = 1 if endpoint else 0
        if t_unit is not None:
            dataset.dims[1].label = t_unit
            

    def add_spiketrains(self, population_name, spiketrains, dataset_names,
                        sourcelist=None, vlen=False):
        """Add a list of spiketrains to the data.

        Add spiketrains listed in `spiketrains` under
        `/data/event/{population_name}/spike` where spiketrain is a
        series of spike times (time elapsed since the start of
        recording when a spike-event occurs). This results in one 1D
        dataset for each spiketrain. The datasets are named as
        specified in `dataset_names`. We look for an existing
        population under `/model/population` with the name
        `population_name`. If found, the spiketrains are assumed to
        have one-to-one correspondence with the members of the
        population and a mapping is created in
        `/map/event/{population_name}`. Otherwise if `sourcelist` is
        specified, then these are the identifiers of the spike
        sources, which can be single neurons in case of point-neuron
        simulation or compartments in case of multicompartmental
        models. We create a population dataset
        `/model/population/{population_name}` containing the entries
        in `sourcelist` and create a mapping dataset
        `/map/event/{population_name}`. If `vlen` is True, we store
        spiketrains as 2D vlen dataset:
        `/data/event/{population_name}/spike`, else as a series of 1D
        datasets under `/data/event/{population_name}/spike` group.
        """
        if sourcelist and (len(sourcelist) != len(spiketrains)):
            raise ValueError('number of sources must match rows in spiketrains')
        try:
            population = self.event_data[population_name]
        except KeyError:
            population = None
        try:
            if population and population['spike']:
                raise ValueError('group with name `spike` already exists')
        except KeyError:
            pass
        try:
            model = self.model_population[population_name]
            if len(model) != len(datalist):
                raise ValueError('size of existing population under %s does not match size of dataset.' %
                                 (self.model_population.path))
            sourcelist = model[:]
        except KeyError:
            if not sourcelist:
                raise ValueError('No source list specified and no existing population with name `%s`'
                                 % (population_name))
            model = None            
        try:
            source_dim = self.event_map[population_name]
        except KeyError:
            if not sourcelist:
                raise ValueError('No population specified and no existing dimension scale population with name `%s`'
                                 % (population_name))
            source_dim = None
        if population is None:
            population = self.event_data.create_group(population_name)
        if vlen:
            dtype = h5.special_dtype(vlen=np.float) # A bug in h5py prevents 64 bit float in vlen
            spike = population.create_dataset('spike', data=spiketrains, dtype=dtype)
        else:
            spike = population.create_group('spike')
            for name, data, src in zip(dataset_names, spiketrains, sourcelist):
                spiketrain = spike.create_dataset(name, data=data, dtype=np.float64)
                spiketrain.attrs['SOURCE'] = src
                if unit is not None:
                    spiketrain.attrs['UNIT'] = unit
        if unit is not None :
            spike.attrs['UNIT'] = unit
        if model is None:
            model = self.model_population.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist])
        # TODO if spike is a group, we need to map the sources with
        # their spiketrain datasets.
        if source_dim is None:
            source_dim = self.uniform_map.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist])
            try:
                spike.dims.create_scale(source_dim, 'source')
                spike.dims[0].attach_scale(source_dim)
            except AttributeError as e:
                # If spike is a group, no attribute called dims.
                pass
            
# 
# NSDFWriter.py ends here
