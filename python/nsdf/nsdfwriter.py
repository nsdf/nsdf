# nsdfwriter.py --- 
# 
# Filename: nsdfwriter.py
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
"""
Writer for NSDF file format.
"""
__author__ = 'Subhasis Ray'
__version__ = '0.1'

import h5py as h5
import numpy as np

from .model import ModelComponent
from .constants import *

class NSDFWriter(object):
    """Writer for NSDF files.

    An NSDF file has three main groups: `/model`, `/data` and `/map`.

    Attributes:
        model (h5.Group): /model group

        data (h5.Group): /data group

        mapping (h5.Group): /map group

        time_dim (h5.Group): /map/time group contains the sampling
            time points as dimension scales of data. It is mainly used
            for nonuniformly sampled data.

        modeltree: (h5.Group): '/model/modeltree group can be used for
            storing the model in a hierarchical manner. Each subgroup
            under `modeltree` is a model component and can contain
            other subgroups representing subcomponents. Each group
            stores the unique identifier of the model component it
            represents in the string attribute `uid`.

    """
    def __init__(self, filename, compression='gzip', compression_opts=6,
                 fletcher32=True, shuffle=True):
        self._fd = h5.File(filename, 'w')
        self.data = self._fd.create_group('/data')
        self.model = self._fd.create_group('/model')
        self.mapping = self._fd.create_group('/map')
        for stype in SAMPLING_TYPES:
            self.data.create_group(stype)
            self.mapping.create_group(stype)
        self.time_dim = self.mapping.create_group('time')
        self.modeltree = self.model.create_group('modeltree')
        self.modelroot = ModelComponent('modeltree', uid='/model/modeltree',
                                        hdfgroup = self.modeltree)
        self.compression = compression
        self.compression_opts = compression_opts
        self.fletcher32 = fletcher32
        self.shuffle = shuffle

    def __del__(self):
        self._fd.close()

    def add_model_component(self, name, uid=None, parent=None,
                            attrs=None):
        """Add a model component to NSDF writer.

        Args:
            name (str): name of the component.
 
            uid (str): unique identifier of the model component. If
                None (default), it uses the full path of the component
                group.
 
            parent (str): path of the group under which to create this
                model component.
 
            attrs (dict): dictionary of attribute names and values.
 
        Returns:
            None

        Raises:
            ValueError

        """
        pass

    def add_model_tree(self, root, target):
        """Add an entire model tree.

        Args:
            root (ModelComponent): root of the source tree.

            target (ModelComponent): target node for the subtree.

        """
        pass

    def add_uniform_ds(self, name, idlist, path_id_dict=None):
        """Add the sources listed in idlist under /map/uniform.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources.

            path_id_dict (dict): (optional) maps the path of the
                source in model tree to the unique id of the source.

        Returns: 
            An HDF5 Dataset storing the source ids. This is
            converted into a dimension scale when actual data is
            added.

        """
        if len(idlist) == 0:
            raise ValueError('idlist must be nonempty')
        base = None
        try:
            base = self.mapping[UNIFORM]
        except KeyError:
            base = self.mapping.create_group(UNIFORM)
        ds = base.create_dataset(name, shape=(len(idlist),), dtype=VLENSTR, data=idlist)
        return ds

    def add_nonuniform_ds(self, name, idlist, homogeneous, path_id_dict=None):
        """Add the sources listed in idlist under /map/nonuniform.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources. This becomes irrelevant if homogeneous=False.

            homogeneous (bool): whether data from all the sources are
                sampled at the same time. If so, we create a single
                dataset for the entire population. Otherwise we create
                a group for the population. The actual mapping tables
                are created when the datasets are added.

            path_id_dict (dict): (optional) maps the path of the
                source in model tree to the unique id of the source.

        Returns: 
            An HDF5 Dataset storing the source ids when
            homogeneous=True. This is converted into a dimension scale
            when actual data is added. If homogeneous=False, the group
            /map/`name` is returned.

        Raises: 
            ValueError if idlist is empty.

        """
        base = None
        if homogeneous and (len(idlist) == 0):
            raise ValueError('idlist must be nonempty for homogeneously sampled population.')
        try:
            base = self.mapping[NONUNIFORM]
        except KeyError:
            base = self.mapping.create_group(NONUNIFORM)
        if homogeneous:
            ds = base.create_dataset(name, shape=(len(idlist),), dtype=VLENSTR, data=idlist)
        else:
            ds = base.create_group(name)
        return ds

    def add_event_ds(self, name, model_paths=None):
        """Create a group under `/map/event` with name `name` to store mapping
        between the datasources and event data.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            model_paths (list): (optional) maps the path of the
                sources in model tree to this group.

        Returns: 
            The HDF5 Group `/map/event/{name}`.
        """
        base = None
        try:
            base = self.mapping[EVENT]
        except KeyError:
            base = self.mapping.create_group(EVENT)
        grp = base.create_group(name)
        return grp

    def add_uniform_data(self, name, 
                         source_ds, source_data_dict,
                         field=None, unit=None,
                         tstart=0.0, dt=0.0, fixed=False):
        """Append uniformly sampled `variable` values from `sources` to
        `data`.

        Args: 
            name (str): name under which this data should be
                stored. Using the variable name whenever possible is
                recommended.

            source_ds (HDF5 Dataset): the dataset storing the source
                ids under map. This is attached to the stored data as
                a dimension scale called `source` on the row
                dimension.

            source_data_dict (dict): a dict mapping source ids to data
                arrays. The data arrays are numpy arrays.

            field (str): name of the recorded variable. Not required
                when appending to existing data.
        
            unit (str): unit of the variable quantity being saved. Not
                required when appending to existing data.

            tstart (double): (optional) start time of this dataset
                recording. Defaults to 0.

            dt (double): (required only for creating new dataset)
                sampling interval.
            
            fixed (bool): if True, the data cannot grow. Default: False

        Returns:
            HDF5 dataset storing the data

        Raises:
            KeyError if the sources in `source_data_dict` do not match
            those in `source_ds`.
        
            IndexError if the data arrays are not all equal in length.

            ValueError if dt is not specified or <= 0 when inserting
            data for the first time.

        """
        popname = source_ds.name.rpartition('/')[-1]
        try:
            ugrp = self.data[UNIFORM][popname]
        except KeyError:
            ugrp = self.data[UNIFORM].create_group(popname)
        src_set = set([src for src in source_ds])
        dsrc_set = set(source_data_dict.keys())
        if src_set != dsrc_set:
            raise IndexError('members of `source_ds` must match keys of'
                           ' `source_data_dict`.')
        ordered_data = [source_data_dict[src] for src in source_ds]
        data = np.vstack(ordered_data)
        try:
            dataset = ugrp[name]
            oldcolcount = dataset.shape[1]
            dataset.resize(oldcolcount + data.shape[1], axis=1)
            dataset[:, oldcolcount:] = data
        except KeyError:
            if dt <= 0.0:
                raise ValueError('`dt` must be > 0.0 for creating dataset.')
            if field is None:
                raise ValueError('`field` is required for creating dataset.')
            if unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            maxcol = None
            if fixed:
                maxcol = data.shape[1]
            dataset = ugrp.create_dataset(name, shape=data.shape,
                                          dtype=data.dtype,
                                          maxshape=(data.shape[0], maxcol),
                                          compression=self.compression,
                                          compression_opts=self.compression_opts,
                                          fletcher32=self.fletcher32,
                                          shuffle=self.shuffle)
            dataset.dims.create_scale(source_ds, 'source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.attrs['tstart'] = tstart
            dataset.attrs['dt'] = dt
            dataset.attrs['field'] = field
            dataset.attrs['unit'] = unit
            
    

# 
# nsdfwriter.py ends here
