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


def match_datasets(hdfds, pydata):
    """Match entries in hdfds with those in pydata. Returns true if the
    two sets are equal. False otherwise.

    """
    src_set = set([item for item in hdfds])
    dsrc_set = set(pydata)
    return src_set == dsrc_set
    
        
class NSDFWriter(object):
    """Writer for NSDF files.

    An NSDF file has three main groups: `/model`, `/data` and `/map`.

    Attributes: 
        mode (str): File open mode. Defaults to append
            ('a'). Can be 'w' or 'w+' also.

        dialect (nsdf.dialect member): ONED for storing nonuniformly
            sampled and event data in 1D arrays.

            VLEN for storing such data in 2D VLEN datasets.

            NANFILLED for storing such data in 2D homogeneous datasets
            with NaN padding.

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
    def __init__(self, filename, dialect=dialect.ONED, mode='a',
                 compression='gzip', compression_opts=6,
                 fletcher32=True, shuffle=True):
        self._fd = h5.File(filename, mode)
        self.mode = mode
        self.dialect = dialect
        try:
            self.data = self._fd['data']
        except KeyError:
            self.data = self._fd.create_group('/data')
        try:
            self.model = self._fd['model']
        except KeyError:
            self.model = self._fd.create_group('/model')
        try:
            self.mapping = self._fd['map']
        except KeyError:
            self.mapping = self._fd.create_group('/map')
        try:
            self.time_dim = self.mapping['time']
        except KeyError:
            self.time_dim = self.mapping.create_group('time')
        try:
            self.modeltree = self.model['modeltree']
        except KeyError:
            self.modeltree = self.model.create_group('modeltree')
        for stype in SAMPLING_TYPES:
            try:
                grp = self.data[stype]
            except KeyError:
                self.data.create_group(stype)
            try:
                grp = self.mapping[stype]
            except KeyError:
                self.mapping.create_group(stype)
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

    def add_nonuniform_ds(self, name, idlist, path_id_dict=None):
        """Add the sources listed in idlist under /map/nonuniform.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources. This becomes irrelevant if homogeneous=False.

            path_id_dict (dict): (optional) maps the path of the
                source in model tree to the unique id of the source.

        Returns:
            An HDF5 Dataset storing the source ids when dialect
            is VLEN or NANFILLED. This is converted into a dimension
            scale when actual data is added. If homogeneous=False, the
            group /map/nonuniform/`name` is returned.

        Raises:
            ValueError if idlist is empty.

        """
        base = None
        if (self.dialect == dialect.ONEDEVENT) and (len(idlist) == 0):
            raise ValueError('idlist must be nonempty for homogeneously sampled population.')
        try:
            base = self.mapping[NONUNIFORM]
        except KeyError:
            base = self.mapping.create_group(NONUNIFORM)
        if self.dialect == dialect.ONED:
            ds = base.create_group(name)
        else:
            ds = base.create_dataset(name, shape=(len(idlist),),
                                     dtype=VLENSTR, data=idlist)
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

    def add_uniform_data(self, name, source_ds, source_data_dict,
                         field=None, unit=None, tstart=0.0, dt=0.0,
                         tunit=None, dtype=np.float64, fixed=False):
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

            tunit (str): (required only for creating new dataset) unit
                of sampling time.

            dtype (numpy.dtype): type of data (default 64 bit float)
            
            fixed (bool): if True, the data cannot grow. Default: False

        Returns:
            HDF5 dataset storing the data

        Raises:
            KeyError if the sources in `source_data_dict` do not match
            those in `source_ds`.
        
            ValueError if dt is not specified or <= 0 when inserting
            data for the first time.

        """
        popname = source_ds.name.rpartition('/')[-1]
        try:
            ugrp = self.data[UNIFORM][popname]            
        except KeyError:
            ugrp = self.data[UNIFORM].create_group(popname)
        if not match_datasets(source_ds, source_data_dict.keys()):
            raise KeyError('members of `source_ds` must match keys of'
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
            if tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            maxcol = None
            if fixed:
                maxcol = data.shape[1]
            dataset = ugrp.create_dataset(
                name, shape=data.shape,
                dtype=dtype,
                data=data,
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
            dataset.attrs['timeunit'] = tunit
        return dataset

    def add_nonuniform_data(self, name, source_ds, source_data_dict,
                            ts, field=None, unit=None,
                            dtype=np.float64, fixed=False):
        """Append nonuniformly sampled `variable` values from `sources` to
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
        if not match_datasets(source_ds, source_data_dict.keys()):
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
            dataset = ugrp.create_dataset(
                name, shape=data.shape,
                dtype=data.dtype,
                data=data,
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
        return dataset

    def add_nonuniform_1d(self, name, source_ds, source_name_dict,
                           source_data_dict, field=None, unit=None,
                           tunit=None, dtype=np.float64, fixed=False):
        """Add nonuniform data when data from each source is in a separate 1D
        dataset.

        For a population of sources called {population}, a group
        `/map/nonuniform/{population}` must be first created (using
        add_nonuniform_ds). This is passed as `source_ds` argument.
        
        When adding the data, the uid of the sources and the names for
        the corresponding datasets must be specified and this function
        will create one dataset for each source under
        `/data/nonuniform/{population}/{name}` where {name} is the
        first argument, preferably the name of the field being
        recorded.
        
        This function can be used when different sources in a
        population are sampled at different time points for a field
        value. Such case may arise when each member of the population
        is simulated using a variable timestep method like CVODE and
        this timestep is not global.

        Args: 
            name (str): name of the group under which data should be
                stored. It is simpler to keep this same as the
                recorded field.

            source_ds (HDF5 Group): the group under `/map/nonuniform`
                created for this population of sources (created by
                add_nonunifrom_ds). The name of this group reflects
                that of the group under `/data/nonuniform` which
                stores the datasets.

            source_name_dict (dict): mapping from source id to dataset
                name.

            source_data_dict (dict): mapping from source id to the
                tuple (data, time) where data contains the recorded
                data points and time contains the sampling times for
                these data points.

            field (str): name of the recorded field. If None, `name`
                is used as the field name.

            unit (str): unit of the data.

            tunit (str): time unit (for the sampling times)

            dtype (numpy.dtype): type of data (default 64 bit float).

            fixed (bool): if True, the data cannot grow. Default:
                False

        Returns:
            dict mapping source ids to the tuple (dataset, time).

        """
        if self.dialect != dialect.ONED:
            raise Exception('add 1D dataset under nonuniform'
                            ' only for dialect=ONED')
        popname = source_ds.name.rpartition('/')[-1]
        try:
            ngrp = self.data[NONUNIFORM][popname]        
        except KeyError:
            ngrp = self.data[NONUNIFORM].create_group(popname)
        assert(len(source_name_dict) == len(source_data_dict),
               'number of sources do not match number of datasets')
        try:
            datagrp = ngrp[name]
        except KeyError:
            datagrp = ngrp.create_group(name)            
        try:
            map_pop = self.mapping[NONUNIFORM][popname]
        except KeyError:
            map_pop = self.mapping[NONUNIFORM].create_group(popname)
        try:
            mapping = map_pop[name]
        except KeyError:
            mapping = map_pop.create_dataset(name,
                                             shape=(len(source_name_dict),),
                                             dtype=SRCDATAMAPTYPE)
        ret = {}
        for ii, source in enumerate(source_data_dict.keys()):
            data, time = source_data_dict[source]
            dsetname = source_name_dict[source]
            try:
                dset = datagrp[dsetname]
                oldlen = dset.shape[0]
                ts = dset.dims[0]['time']
                dset.resize(oldlen + len(data))
                dset[oldlen:] = data
                ts.resize(oldlen + len(data))
                ts[oldlen:] = time
            except KeyError:
                if field is None:
                    raise ValueError('`field` is required for creating dataset.')
                if unit is None:
                    raise ValueError('`unit` is required for creating dataset.')
                if tunit is None:
                    raise ValueError('`tunit` is required for creating dataset.')
                maxcol = len(data) if fixed else None
                dset = datagrp.create_dataset(dsetname,
                                              shape=(len(data),),
                                              dtype=dtype, data=data,
                                              maxshape=(maxcol,),
                                              compression=self.compression,
                                              compression_opts=self.compression_opts,
                                              fletcher32=self.fletcher32,
                                              shuffle=self.shuffle)
                dset.attrs['unit'] = unit
                dset.attrs['field'] = field
                dset.attrs['source'] = source
                mapping[ii]['source'] = source
                mapping[ii]['data'] = dset.ref
                # Using {popname}_{variablename}_{dsetname} for
                # simplicity. What about creating a hierarchy?
                tsname = '{}_{}_{}'.format(popname, name, dsetname)
                ts = self.time_dim.create_dataset(tsname,
                                                  shape=(len(data),),
                                                  dtype=np.float64,
                                                  data=time,
                                                  compression=self.compression,
                                                  compression_opts=self.compression_opts,
                                                  fletcher32=self.fletcher32,
                                                  shuffle=self.shuffle)
                dset.dims.create_scale(ts, 'time')
                dset.dims[0].label = 'time'
                dset.dims[0].attach_scale(ts)
                ts.attrs['unit'] = tunit
            ret[source] = (dset, ts)
        return ret
    
    def add_nonuniform_vlen(self, name, source_ds, source_data_dict,
                            field=None, unit=None, tunit=None,
                            dtype=np.float64, fixed=False):
        """Add nonuniform data when data from all sources in a population is
        stored in a 2D ragged array.

        When adding the data, the uid of the sources and the names for
        the corresponding datasets must be specified and this function
        will create the dataset `/data/nonuniform/{population}/{name}`
        where {name} is the first argument, preferably the name of the
        field being recorded.
        
        This function can be used when different sources in a
        population are sampled at different time points for a field
        value. Such case may arise when each member of the population
        is simulated using a variable timestep method like CVODE and
        this timestep is not global.

        Args: 
            name (str): name of the group under which data should be
                stored. It is simpler to keep this same as the
                recorded field.

            source_ds (HDF5 dataset): the dataset under
                `/map/nonuniform` created for this population of
                sources (created by add_nonunifrom_ds).

            source_data_dict (dict): mapping from source id to the
                tuple (data, time) where data contains the recorded
                data points and time contains the sampling times for
                these data points.

            field (str): name of the recorded field. If None, `name`
                is used as the field name.

            unit (str): unit of the data.

            tunit (str): time unit (for the sampling times)

            dtype (numpy.dtype): type of data (default 64 bit float).

            fixed (bool): if True, this is a one-time write and the
                data cannot grow. Default: False

        Returns:
            tuple containing HDF5 Datasets for the data and sampling
            times.

        TODO: 
            Concatenating old data with new data and reassigning is a poor
            choice. waiting for response from h5py mailing list about
            appending data to rows of vlen datasets. If that is not
            possible, vlen dataset is a technically poor choice.

        """
        if self.dialect != dialect.VLEN:
            raise Exception('add 2D vlen dataset under nonuniform'
                            ' only for dialect=VLEN')
        popname = source_ds.name.rpartition('/')[-1]
        try:
            ngrp = self.data[UNIFORM][popname]            
        except KeyError:
            ngrp = self.data[UNIFORM].create_group(popname)
        if not match_datasets(source_ds, source_data_dict.keys()):
            raise KeyError('members of `source_ds` must match keys of'
                           ' `source_data_dict`.')
        try:
            dataset = ngrp[name]
        except KeyError:
            if field is None:
                raise ValueError('`field` is required for creating dataset.')
            if unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            if tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            vlentype = h5.special_dtype(vlen=dtype)
            # Fix me: is there any point of keeping the compression
            # and shuffle options?
            dataset = ngrp.create_dataset(name, shape=source_ds.shape,
                                          dtype=vlentype,
                                          compression=self.compression,
                                          compression_opts=self.compression_opts,
                                          fletcher32=self.fletcher32,
                                          shuffle=self.shuffle)
            dataset.attrs['field'] = field
            dataset.attrs['unit'] = unit
            dataset.dims.create_scale(source_ds, 'source')
            dataset.dims[0].attach_scale(source_ds)
            # Using {popname}_{variablename} for simplicity. What
            # about creating a hierarchy?
            tsname = '{}_{}'.format(popname, name)
            # fixme: VLENFLOAT should be made VLENDOUBLE whenever h5py
            # fixes it
            time_ds = self.time_dim.create_dataset(tsname,
                                                  shape=dataset.shape,
                                                  dtype=VLENFLOAT,      
                                                  compression=self.compression,
                                                  compression_opts=self.compression_opts,
                                                  fletcher32=self.fletcher32,
                                                  shuffle=self.shuffle)
            dataset.dims.create_scale(time_ds, 'time')
            dataset.dims[0].attach_scale(time_ds)
            time_ds.attrs['unit'] = tunit
        for ii, source in enumerate(source_ds):
            data, time = source_data_dict[source]
            dataset[ii] = np.concatenate((dataset[ii], data))
            time_ds[ii] = np.concatenate((time_ds[ii], time))            
        return dataset, time_ds


    
# 
# nsdfwriter.py ends here
