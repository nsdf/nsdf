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
from collections import Sequence

class NSDFWriter(object):
    """Writer of NSDF files."""
    def __init__(self, filename):
        self._fd = h5.File(filename, 'w')
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

    def add_uniform_dataset(self, population_name, datalist, dataset_name,
                            **kwargs):
        """Add a uniformly sampled dataset to the file. 

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
            
            dtype: (optional) dtype to be used for floating point
                data. This is essentially for precision, can be either
                np.float32 or np.float64. Default is np.float64 but is
                switched to np.float32 for vlen arrays to bypass an h5py bug.            
            
            Any additional kwyord arguments are passed to
            h5py.create_dataset as is. These can include
            `compression`, `compression_opts`, `shuffle` and
            `fletcher32`.

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
        sourcelist = kwargs.pop('sourcelist', None)
        times = kwargs.pop('times', None)
        t_start = kwargs.pop('t_start', 0.0)
        t_end = kwargs.pop('t_end', None)
        endpoint = kwargs.pop('endpoint', False)
        unit = kwargs.pop('unit', None)
        t_unit = kwargs.pop('t_unit', None)
        dtype = kwargs.pop('dtype', np.float64)
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
            
        dataset = population.create_dataset(dataset_name, data=datalist, dtype=np.float64, **kwargs)
        if unit is not None:
            dataset.attrs['UNIT'] = unit

        if model is None:
            model = self.model_population.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist], **kwargs)
        if source_dim is None:
            source_dim = self.uniform_map.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist], **kwargs)
            dataset.dims.create_scale(source_dim, 'source')
            dataset.dims[0].attach_scale(source_dim)
        if times:
            try:
                time_pop =  self.uniform_time_dim[population_name]
            except KeyError:
                time_pop = self.uniform_time_dim.create_group(population_name)
            time_dim = time_pop.create_dataset(dataset_name, data=times, dtype=dtype, **kwargs)
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
            
    def add_nonuniform_dataset(self, population_name, datalist,
                               variable_name, times,
                               **kwargs):
        """Add nonuniformly sampled dataset to the file. 

        Save nonuniformly sampled dataset in the NSDF file. This has
        two possible behaviours depending on the nature of dataset
        name. 

        If `dialect` is `vlen`, this will create a 2D dataset
        /data/nonuniform/{population_name}/{variable_name}, first
        creating the group {population_name} if not already present.
        If `sourcelist` is specified, it will create a new dataset
        containing the entries in `sourcelist` under
        /model/population/{population_name} if required. It also
        creates a dimension scale /map/nonuniform/{population_name}
        and attaches this to the first dimension (rows) of the
        dataset. If `times` is a single array, all rows in the dataset
        share the same sampling times and the dataset is a fixed
        length 2D array. `times` will be stored as a dimension scale
        /map/time/nonuniform/{population_name}/{variable_name}
        creating the group {population_name} if required and will
        attach it to the second dimension (columns). On the other
        hand, if each row in the dataset has different sampling times,
        then times will be list of arrays not necessarily of the same
        length. The dataset `dataset_name` in this case is a vlen
        dataset. Then create a 2D vlen dataset
        /map/time/nonuniform/{population_name} which has one to one
        mapping with
        /data/nonuniform/{population_name}/{variable_name}.

        If `dialect` is `1d`, we store each array in datalist as a
        separate 1D dataset with the name taken from the corresponding
        entry in `dataset_names` (or an increasing sequence of
        unsigned integers if not specified) under
        /data/nonuniform/{population_name}/{variable_name} group,
        creating the it first if not already present. In this case, if
        `times` is a single array, all datasets share the same
        sampling times and we create a single dimension scale
        /map/time/nonuniform/{population_name}/{variable_name} and
        attach it to the first dimension of all the
        datasets. Otherwise `times` must be a list of arrays with same
        number of entries as in `datalist`. For each 1D dataset
        {dataset_name} we create a 1D dimension scale containing the
        corresponding array in `times` and attach the latter as a
        dimension scale to the first dimension of the dataset.

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

            datalist: a 2D numpy array of doubles (64 bit float). 

            variable_name: string specifying the name of the variable
                being recorded.

            dataset_names: (optional) in case of 1d datasets use these
                names for the datasets. If unspecified, sequential
                integers are used.
        
            times: float array of sampling times or a list of such
                arrays, in which case it must match the datalist in all
                dimensions.

            sourcelist: list of string specifying the source object
                identifiers. An object identifier can be any string.
                If None or unspecified, a population with name 
                `population_name` must already exist in 
                `/model/population` as well as `/map/uniform`.
                default: None

            unit: (optional) string specifying the unit of the
                quantity. If specified, this will be stored in the `UNIT`
                attribute of the dataset.

            t_unit: (optional) string specifying the unit of time in
                sampling time. If specified, this is stored in the
                label of the second dimension of the
                dataset. Moreover, if a dimension scale is created for
                sampling times, then that also gets this value in its
                UNIT attribute.

            dtype: (optional) dtype to be used for floating point
                data. This is essentially for precision, can be either
                np.float32 or np.float64. Default is np.float64 but is
                switched to np.float32 for vlen arrays to bypass an h5py bug.            

            dialect: (optional) string specifying one of the
                alternatives of storing nonuniformly sampled data. If
                `1d`, then a group is created with the name of the
                population and then one 1D dataset under it stores data
                from each datasource. If `vlen` is specified then a vlen
                2D dataset with the name of the population is created
                where each row stores data from one data source. In this
                case a dimension scale is created with the list of data
                source identifiers and this is attached to the row
                dimension of the vlen dataset. Note that in this case we
                are forced to store the data as single precision floating
                point to avoid a bug in h5py.
                
            Any additional kwyord arguments are passed to
            h5py.create_dataset as is. These can include
            `compression`, `compression_opts`, `shuffle` and
            `fletcher32`.

        # NOTE possible combinations
        N - 1D data arrays, N - 1D time arrays (most generic)
        N - 1D data arrays, 1 - 1D time array
        1 - 2D data array, 1 - 1D time array
        1 - 2D ragged data array, 1 - 2D ragged time array
        1 - 2D data array with NaN filling the extra columns.

        TODO: This complicated design is to allow creating examples
        according to different proposals for NSDF. Once we settle on a
        specification, it should be simplified.

        Returns:
            None

        Raises:
            ValueError: sourcelist and dataset length do not match.
                or population of name `population_name` exists but the length does not match 
                or sourcelist is unspecified and no population of name `population_name` exists
                or sourcelist is unspecified and no dimension scale of name `population_name` exists
                or dataset already exists

        """
        dataset_names = kwargs.pop('dataset_names', None)
        sourcelist = kwargs.pop('sourcelist', None)
        unit = kwargs.pop('unit', None)
        t_unit = kwargs.pop('t_unit', None)
        dtype = kwargs.pop('dtype', np.float64)
        dialect = kwargs.pop('dialect', '1d')
        dialect = dialect.lower()
        if sourcelist and (len(sourcelist) != len(datalist)):
            raise ValueError('number of sources must match rows in datalist')
        try:
            iter(times[0])
            shared_t = False
        except TypeError:
            shared_t = True
        if not shared_t:            
            for t, data in zip(times, datalist):
                if len(t) != len(data):
                    raise ValueError('number of timepoints specified must match number of entries in data')
        if dataset_names and (len(dataset_names) != len(datalist)):
            raise ValueError('number of names must be same as that of datasets.')
        try:
            time_pop = self.nonuniform_time_dim[population_name]
        except KeyError:
            time_pop = self.nonuniform_time_dim.create_group(population_name)
        try:
            population = self.nonuniform_data[population_name]
        except KeyError:
            if not sourcelist:
                raise ValueError('either sourcelist should be specified or population must exist.')
            population = self.nonuniform_data.create_group(population_name)
        try:
            variable = population[variable_name]
        except KeyError:
            # N - 1D data + N - 1D times
            if dialect == '1d':                
                variable = population.create_group(variable_name)
            else: #
                if shared_t:    # fixed length dataset with one time dimscale
                    variable = population.create_dataset(variable_name,
                                                         data=datalist,
                                                         dtype=dtype, **kwargs)
                    time_dim = time_pop.create_dataset(variable_name,
                                                       data=times,
                                                       dtype=dtype, **kwargs)
                    if t_unit:
                        tdim.attrs['UNIT'] = t_unit
                    variable.dims.create_scale(time_dim, 'time')
                    variable.attach_scale(time_dim)
                else:    # variable length dataset
                    variable = population.create_dataset(variable_name,
                                                         shape=(len(datalist),),
                                                         dtype=h5.special_dtype(vlen='float32'), **kwargs)    # TODO make this float64 once h5py bug is fixed
                    time_dim = time_pop.create_dataset(variable_name, shape=(len(datalist),),
                                                       dtype=h5.special_dtype(vlen='float32'), **kwargs)    # TODO make this float64 once h5py bug is fixed
                    if t_unit:
                        tdim.attrs['UNIT'] = t_unit
                    for ii in range(len(datalist)):                                    
                        variable[ii] = data
                        time_dim[ii] = times[ii]
        if isinstance(variable, h5.Dataset) and unit:
            variable.attrs['UNIT'] = unit
        if dialect == '1d':            
            if shared_t:
                time_dim = time_pop.create_dataset(variable_name, data=times,
                                                   dtype=np.float64, **kwargs)
                if t_unit:
                    tdim.attrs['UNIT'] = t_unit
            else:
                time_dim = time_pop.create_group(variable_name)
            # this assumes the dataset names can be different for
            # different variables and we need to store the full path
            # of each variable
            source_group = self.nonuniform_map.create_group(population_name)
            source_dim = source_group.create_dataset(variable_name,
                                                     shape=(len(datalist),),
                                                     dtype=np.dtype([('source', 'S1024'), ('data', 'S1024')]),
                                                     **kwargs)
            if dataset_name is None:
                dataset_names = [str(ii) for ii in range(len(datalist))]
            for ii in range(len(datalist)):
                name, data = dataset_names[ii], datalist[ii]
                dataset = variable.create_dataset(name, data=data, dtype=dtype, **kwargs)
                if unit:
                    dataset.attrs['UNIT'] = unit
                dataset.attrs['source'] = sourcelist[ii]
                source_dim[ii] = (str(sourcelist[ii]), str(dataset.name))
                if shared_t:
                    tdim =time_dim
                else:
                    tdim = time_dim.create_dataset(name, data=times[ii], dtype=dtype, **kwargs)
                    if t_unit:
                        tdim.attrs['UNIT'] = t_unit
                dataset.dims.create_scale(tdim, 'time')
                dataset.dims[0].attach_scale(tdim)           

    def add_spiketrains(self, population_name,
                        spiketrains,
                        **kwargs):
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

        Args: 
            population_name: string, name of the population from which
                the spiketrains were recorded.

            spiketrains: list of spiketrains where each spiketrain is
                an sequence of floats representing spike times.

            dataset_names: (optional) list of strings. If this is
                specified then each spiketrain is stored as a 1D
                dataset under the group
                `/data/event/{population_name}/spike`. Otherwise, all
                the spiketrains are stored as a 2D vlen dataset where
                each row contains one spiketrain.

            sourcelist: (optional) list of strings identifying the
                source of each spike train. If unspecified, there must
                be an entry for {population_name} under `/map/event`
                with the same number of entries as in `spiketrains`. A
                one-to-one correspondence is assumed between this and
                the spiketrains.

            unit: (optional) string specifying the unit of time used
                in the spiketrains.

            dtype: (optional) dtype to be used for floating point
                data. This is essentially for precision, can be either
                np.float32 or np.float64. Default is np.float64 but is
                switched to np.float32 for vlen arrays to bypass an h5py bug.            

            dialect: (optional) string specifying one of the
                alternatives of storing nonuniformly sampled data. The
                options are: `1d`, `vlen` and `nan`

                If `1d`, then a group is created with the name of the
                population and then one 1D dataset under it stores
                data from each datasource. If `vlen` is specified then
                a vlen 2D dataset with the name of the population is
                created where each row stores data from one data
                source. In this case a dimension scale is created with
                the list of data source identifiers and this is
                attached to the row dimension of the vlen
                dataset. Note that in this case we are forced to store
                the data as single precision floating point to avoid a
                bug in h5py. If `nan`, then we create a homogeneous 2D
                array (with the same name as the population) with as
                many columns as the number of entries in the longest
                dataset. Data from each source is stored in a row and
                if the number of valid entries are less than the
                number of columns then we pad it with NaN to the
                right. A dimension scale containing the list of source
                identifiers is attached to the row dimension of the
                dataset.
                
            Any additional kwyord arguments are passed to
            h5py.create_dataset as is. These can include
            `compression`, `compression_opts`, `shuffle` and
            `fletcher32`.

        Returns: None

        Raises: 
            ValueError: if number of sources do not match that of spiketrains.
                        the group `/data/event/{population_name}/spie` alreadt exists.
                        the dataset `/model/population/{population_name}` exists but has different length from the number of spiketrains.
                        population `population_name` does not exist and no `sourcelist` was specified.

        """
        dataset_names = kwargs.pop('dataset_names', None)
        sourcelist = kwargs.pop('sourcelist', None)
        unit = kwargs.pop('unit', None)
        dtype = kwargs.pop('dtype', np.float64)
        dialect = kwargs.pop('dialect', '1d')
        dialect = dialect.lower()
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
            source_group = self.event_map[population_name]
        except KeyError:
            if not sourcelist:
                raise ValueError('No population specified and no existing dimension scale population with name `%s`'
                                 % (population_name))
            source_group = self.event_map.create_group(population_name)
        if population is None:
            population = self.event_data.create_group(population_name)
        if dialect == 'vlen':
            dtype = h5.special_dtype(vlen='float32') # A bug in h5py prevents 64 bit float in vlen
            spike = population.create_dataset('spike', shape=(len(spiketrains),), dtype=dtype, **kwargs)
            for ii, train in enumerate(spiketrains):
                spike[ii] = train
        elif dialect == 'nan':
            spike = population.create_dataset('spike',
                                              shape=(len(spiketrains), max([len(train) for train in spiketrains])),
                                              dtype=dtype, **kwargs)
            for ii, train in enumerate(spiketrains):
                spike[ii] = train
                spike[ii,len(train):] = np.nan
            
        else: # dialect == '1d':
            source_dim = source_group.create_dataset('spike',
                                                     shape=(len(dataset_names),),
                                                     dtype=np.dtype([('source', 'S1024'), ('data', 'S1024')]))
            spike = population.create_group('spike')
            if dataset_names is None:
                dataset_names = [str(ii) for ii in range(len(spiketrains))]
            for ii in range(len(dataset_names)):
                name, data, src  = dataset_names[ii], spiketrains[ii], sourcelist[ii]
                spiketrain = spike.create_dataset(name, data=data, dtype=dtype, **kwargs)
                spiketrain.attrs['SOURCE'] = src
                if unit is not None:
                    spiketrain.attrs['UNIT'] = unit
                source_dim[ii] = (sourcelist[ii], spiketrain.name)
            
        if unit is not None :
            spike.attrs['UNIT'] = unit
        if model is None:
            model = self.model_population.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist], **kwargs)
        # If spike is a group, we need to map the sources with their
        # spiketrain datasets. One possibility is to name the datasets
        # with integers which represent the index of the source in
        # sourcelist. Another, more general way is to create a 2 column
        # dataset mapping each source to its dataset.
        if source_dim is None:
            source_dim = self.event_map.create_dataset(population_name,
                                                         dtype=h5.special_dtype(vlen=str),
                                                         data=[str(src) for src in sourcelist],
                                                       **kwargs)
            try:
                spike.dims.create_scale(source_dim, 'source')
                spike.dims[0].attach_scale(source_dim)
            except AttributeError as e:
                # If spike is a group, no attribute called dims.
                pass
            
# 
# NSDFWriter.py ends here
