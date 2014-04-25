# NSDFWriter.py --- 
# 
# Filename: NSDFWriter.py
# Description: 
# Author: Subhasis Ray
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

    def add_uniform_dataset(self, population_name, dataset_name, datalist,
                            sourcelist=None, times=None, t_start=0.0, t_end=None, endpoint=False):
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

        if model is None:
            model = self.model_population.create_dataset(population_name, dtype=h5.special_dtype(vlen=str), data=[str(src) for src in sourcelist])
        if source_dim is None:
            source_dim = self.uniform_map.create_dataset(population_name, dtype=h5.special_dtype(vlen=str), data=[str(src) for src in sourcelist])
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
        elif t_end is not None:
            dataset.attrs['t_start'] = t_start
            dataset.attrs['t_end'] = t_end
            if endpoint:
                dataset.attrs['endpoint'] = 1
            else:
                dataset.attrs['endpoint'] = 0

            
# 
# NSDFWriter.py ends here
