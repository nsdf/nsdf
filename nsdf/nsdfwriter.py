# nsdfwriter.py --- 
# 
# Filename: nsdfwriter.py
# Description: 
# Author: Subhasis Ray [email: {lastname} dot {firstname} at gmail dot com]
# Maintainer: 
# Created: Fri Apr 25 19:51:42 2014 (+0530)

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

try:
    from builtins import next
    from builtins import str
    from builtins import zip
    from builtins import range
    from builtins import object
except ImportError as e:
    from __builtin__ import next
    from __builtin__ import str
    from __builtin__ import zip
    from __builtin__ import range
    from __builtin__ import object

import h5py as h5
import numpy as np
import os
import warnings

from .model import ModelComponent, common_prefix
from .constants import *
from .util import *
from datetime import datetime

def match_datasets(hdfds, pydata):
    """Match entries in hdfds with those in pydata. Returns true if the
    two sets are equal. False otherwise.

    """
    # HDF5 VLEN string are represented as byte objects in h5py
    strinfo = None
    if isinstance(hdfds, h5.Dataset):
        strinfo = h5.check_string_dtype(hdfds.dtype)
    if strinfo is None:
        src_set = set([item for item in hdfds])
    else:
        src_set = set([item.decode(strinfo.encoding) for item in hdfds])
    dsrc_set = set(pydata)
    return src_set == dsrc_set


def add_model_component(component, parentgroup):
    """Add a model component as a group under `parentgroup`. 

    This creates a group `component.name` under parent group if not
    already present. The `uid` of the component is stored in the `uid`
    attribute of the group. Key-value pairs in the `component.attrs`
    dict are stored as attributes of the group.

    Args: 
        component (ModelComponent): model component object to be
            written to NSDF file.

        parentgroup (HDF Group): group under which this
            component's group should be created.

    Returns:
        HDF Group created for this model component.

    Raises: 
        KeyError if the parentgroup is None and no group
        corresponding to the component's parent exists.

    """
    grp = parentgroup.require_group(component.name)
    component.hdfgroup = grp
    if component.uid is not None:
        grp.attrs['uid'] = component.uid
    else:
        grp.attrs['uid'] = component.path
    for key, value in list(component.attrs.items()):
        grp.attrs[key] = value
    return grp


def write_ascii_file(group, name, fname, **compression_opts):
    """Add a dataset `name` under `group` and store the contents of text
    file `fname` in it."""
    with open(fname, 'rt') as fhandle:
        data = fhandle.read()            
    if '\x00' in data:
        raise ValueError('Cannot handle NULL byte in ascii data')
    dataset = group.create_dataset(name, shape=(1,), data=data, dtype=VLENBYTE,
                                   **compression_opts)
    return dataset


def write_binary_file(group, name, fname, **compression_opts):
    """Add a dataset `name` under `group` and store the contents of binary
    file `fname` in it."""
    with open(fname, 'rb') as fhandle:
        data = np.void(fhandle.read())
    dataset = group.create_dataset(name, shape=(1,), data=data, dtype=np.void)
    return dataset


def write_dir_contents(root_group, root_dir, ascii, **compression_opts):
    """Walk the directory tree rooted at `root_dir` and replicate it under
    `root_group` in HDF5 file. 

    This is a helper function for copying model directory structure
    and file contents into an hdf5 file. If ascii=True all files are
    considered ascii text else all files are taken as binary blob.

    Args:

        root_group (h5py.Group): group under which the directory tree
            is to be created.

        root_dir (str): path of the directory from which to start
           traversal.

        ascii (bool): whether to treat each file as ascii text file.

    """
    for root, dirs, files in os.walk(root_dir):
        relative_root = root[root.find(os.path.basename(root_dir)):]
        grp = root_group.require_group(relative_root)
        for fname in files:
            dset_name = os.path.basename(fname)
            file_path = os.path.join(root, fname)
            if ascii:
                try:
                    dset = write_ascii_file(grp, dset_name, file_path, **compression_opts)
                except ValueError:
                    warnings.warn('Skipping binary file {}'.format(file_path))
            else:
                dset = write_binary_file(grp, dset_name, file_path, **compression_opts)


class NSDFWriter(object):
    """Writer for NSDF files.

    An NSDF file has three main groups: `/model`, `/data` and `/map`.

    Attributes: 
        mode (str): File open mode. Defaults to append
            ('a'). Can be 'w' or 'w+' also.

        dialect (nsdf.dialect member): ONED for storing nonuniformly
            sampled and event data in 1D arrays.

            VLEN for storing such data in 2D VLEN datasets.

            NANPADDED for storing such data in 2D homogeneous datasets
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
    def __init__(self, filename, dialect=dialect.ONED, mode='a', **h5args):
        """Initialize NSDF writer.

        Args:

            filename (str): path of the file to be written.

            dialect (nsdf.dialect member): the dialect of NSDF to be
                used. Default: ONED.

            mode (str): file write mode. Default is 'a', which is also
                the default of h5py.File.

            **h5args: other keyword arguments are passed to h5py when
                  creating datasets. These can be `compression`
                  (='gzip'/'szip'/'lzf'), `compression_opts` (=0-9
                  with gzip), `fletcher32` (=True/False), `shuffle`
                  (=True/False).

        """
        self.filename = filename
        self._fd = h5.File(filename, mode)
        self.timestamp = datetime.utcnow()
        self._fd.attrs['created'] = self.timestamp.isoformat()
        self._fd.attrs['nsdf_version'] = '0.1'
        self._fd.attrs['dialect'] = dialect
        self.mode = mode
        self.dialect = dialect
        self.data = self._fd.require_group('/data')
        self.model = self._fd.require_group('/model')
        self.mapping = self._fd.require_group('/map')
        self.time_dim = self.mapping.require_group('time')
        self.modeltree = self.model.require_group('modeltree')
        for stype in SAMPLING_TYPES:
            self.data.require_group(stype)
            self.mapping.require_group(stype)
        self.modelroot = ModelComponent('modeltree', uid='modeltree',
                                        hdfgroup=self.modeltree)
        self.h5args = h5args

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, traceback):
        self._fd.close()

    def close(self):
        self._fd.close()

    def set_properties(self, properties):
        """Set the file attributes (environments).

        Args:
            properties (dict): mapping property names to values.
                It must contain the following keyes:

                title (str)
                creator (list of str)
                software (list of str)
                method (list of str)
                description (str)
                rights (str)
                tstart (datetime.datetime)
                tend (datetime.datetime)
                contributor (list of str)
                

        Raises:
            KeyError if not all environment properties are specified in the dict.

        """
        self._fd.attrs['title'] = properties['title']
        attr = np.zeros((len(properties['creator']),), dtype=VLENSTR)
        attr[:] = properties['creator']
        self._fd.attrs['creator'] = attr                
        attr = np.zeros((len(properties['software']),), dtype=VLENSTR)
        attr[:] = properties['software']
        self._fd.attrs['software'] = attr
        attr = np.zeros((len(properties['method']),), dtype=VLENSTR)
        attr[:] = properties['method']
        self._fd.attrs['method'] = attr                
        self._fd.attrs['description'] = properties['description']
        self._fd.attrs['rights'] = properties['rights']
        self._fd.attrs['tstart'] = properties['tstart'].isoformat()
        self._fd.attrs['tend'] = properties['tend'].isoformat()
        attr = np.zeros((len(properties['contributor']),), dtype=VLENSTR)
        attr[:] = properties['contributor']
        self._fd.attrs['contributor'] = attr                
        
        

    @property
    def title(self):
        """Title of the file"""
        try:
            return self._fd.attrs['title']
        except KeyError:
            return None

    @title.setter
    def title(self, title):
        """Set the title of the file.

        Args:
            title (str): title text of the file.

        """
        self._fd.attrs['title'] = title

    @property
    def creator(self):
        return self._fd.attrs['creator']
        
    @creator.setter
    def creator(self, creator_list):
        """Set the creator (one or more authors) of the file.

        Args:
            creator_list (list of str): list of creators of the file.

        """
        if isinstance(creator_list, str):
            creator_list = [creator_list]
        attr = np.zeros((len(creator_list),), dtype=VLENSTR)
        attr[:] = creator_list
        self._fd.attrs['creator'] = attr                

    @property
    def license(self):
        """License information about the file. This is text string."""
        return self._fd.attrs['license']

    @license.setter
    def license(self, text):
        self._fd.attrs['license'] = text

    @property
    def software(self):
        """Software (one or more) used to generate the data in the file.

        """
        return self._fd.attrs['software']

    @software.setter
    def software(self, software_list):       
        """Set the software (one or more) used to generate the data in the
        file.

        Args:
            software_list (list of str): list of software that
                involved in generating the data in the file.

        """
        if isinstance(software_list, str):
            software_list = [software_list]        
        attr = np.zeros((len(software_list),), dtype=VLENSTR)
        attr[:] = software_list
        self._fd.attrs['software'] = attr

    @property
    def method(self):
        """(numerical) methods applied in generating the data."""
        return self._fd.attrs['method']

    @method.setter
    def method(self, method_list):
        """Set the (numerical) methods applied in generating the data.

        Args:
            method_list (list of str): names of the methods employed
                to generate the data.

        """
        if isinstance(method_list, str):
            method_list = [method_list]
        attr = np.zeros((len(method_list),), dtype=VLENSTR)
        attr[:] = method_list
        self._fd.attrs['method'] = attr                

    @property
    def description(self):
        """Description of the file. A text string."""
        return self._fd.attrs['description']

    @description.setter
    def description(self, description):
        """Set the description of the file.

        Args:
            description (str): a human readable description of the
                file.

        """
        self._fd.attrs['description'] = description

    @property
    def rights(self):
        """The rights of the file contents."""
        return self._fd.attrs['rights']

    @rights.setter
    def rights(self, rights):
        """Set the rights of the file contents.

        Args:
            rights (str): text describing the rights of various
                individuals/organizations/other entities on the file
                contents.

        """
        self._fd.attrs['rights'] = rights

    @property
    def tstart(self):
        """Start time of the simulation / data recording. A string
        representation of the timestamp in ISO format

        """
        return self._fd.attrs['tstart']

    @tstart.setter    
    def tstart(self, tstart):
        """Set the start time of simulation/recording

        Args:
            tstart (datetime.datetime): start date-time of the data
                recording/simulation. 

        Note:
            We take datetime instance here because we want to ensure ISO format.

        """
        self._fd.attrs['tstart'] = tstart.isoformat()

    @property
    def tend(self):
        """End time of the simulation/recording."""
        return self._fd.attrs['tend']

    @tend.setter
    def tend(self, tend):
        """Set the end time of recording/simulation.

        Args: 
            tend (datetime.datetime): end date-time of the data
                recording or simulation.

        Note:
            We take datetime instance here because we want to ensure ISO format.

        """
        self._fd.attrs['tend'] = tend.isoformat()

    @property
    def contributor(self):
        """List of contributors to the content of this file."""
        return self._fd.attrs['contributor']

    @contributor.setter
    def contributor(self, contributor_list):
        """Set the list of contributors to the contents of the file.

        Args: 
            contributor_list (list of str): list of
                individuals/organizations/other entities who
                contributed towards the data stored in the file.

        """
        if isinstance(contributor_list, str):
            contributor_list = [contributor_list]
        attr = np.zeros((len(contributor_list),), dtype=VLENSTR)
        attr[:] = contributor_list
        self._fd.attrs['contributor'] = attr                
        

    def _link_map_model(self, mapds):
        """Link the model to map dataset and vice versa. 

        The map dataset stores a list of references to the closest
        common ancestor of all the source components in it in the
        attribute `model`. The closest common ancestor in the model
        tree also stores a reference to this map dataset in its `map`
        attribute.

        This is an internal optimization in NSDF because given that
        every model component has an unique id and the map datasets
        store these unique ids, it is always possible to search the
        entire mdoel tree for these unique ids.
    
        Args:
            mapds: The map dataset for which the linking should be done.

        Returns:
            None

        """
        self.modelroot.update_id_path_dict()
        id_path_dict = self.modelroot.get_id_path_dict()
        if mapds.dtype.fields is None:
            idlist = mapds
        else:
            idlist = mapds['source']
            
        if len(id_path_dict) > 1:
            # there are elements other than /model/modeltree
            paths = []
            for uid in idlist:
                try:
                    paths.append(id_path_dict[uid])
                except KeyError:
                    warnings.warn('modeltree does not include '
                                  'source id {} in the DS'.format(uid))
            prefix = common_prefix(paths)[len('/modeltree/'):]
            if not prefix:
                warnings.warn('no common prefix for map dimscale {}'.format(
                    mapds.name))
                return
            try:
                source = self.modeltree[prefix]
                tmpattr = ([ref for ref in source.attrs.get('map', [])]
                           + [mapds.ref])
                attr = np.zeros((len(tmpattr),), dtype=REFTYPE)
                attr[:] = tmpattr
                source.attrs['map'] = attr
                tmpattr = ([ref for ref in mapds.attrs.get('map', [])]
                           + [source.ref])
                attr = np.zeros((len(tmpattr),), dtype=REFTYPE)
                attr[:] = tmpattr
                mapds.attrs['model'] = attr                
            except KeyError as error:
                warnings.warn(error.message)
        
    def add_modeltree(self, root, target='/'):
        """Add an entire model tree. This will cause the modeltree rooted at
        `root` to be written to the NSDF file.

        Args:
            root (ModelComponent): root of the source tree.

            target (str): target node path in NSDF file with respect
                to '/model/modeltree'. `root` and its children are
                added under this group.

        """
        def write_absolute(node, rootgroup):
            """Write ModelComponent `node` at its path relative to `rootgroup`.
            """
            if node.parent is None:
                parentgroup = rootgroup
            else:
                parentpath = node.parent.path[1:] 
                parentgroup = rootgroup[parentpath]
            add_model_component(node, parentgroup)
            
        node = self.modelroot
        # Get the node corresponding to `target`, traverse by
        # splitting to avoid confusion between absolute and relative
        # paths.
        for name in target.split('/'):
            if name:
                node = node.children[name]
        node.add_child(root)
        self.modelroot.visit(write_absolute, self.model)

    def add_model_filecontents(self, filenames, basedir, ascii=True, recursive=True):
        """Add the files and directories listed in `filenames` to
        ``/model/filecontents``.
        
        This function is for storing the contents of model files in
        the NSDF file. In case of external formats like NeuroML,
        NineML, SBML and NEURON/GENESIS scripts, this function is
        useful. Each directory is stored as a group and each file is
        stored as a dataset.

        Args: 
            filenames (sequence): the paths of files and/or
                directories which contain model information.

            basedir (str): path of the basedirectory of the model. 
                This is necessary to avoid problem with nonunix file 
                paths like `C:\\mydir\\xyz.py` and relative paths with `..`

            ascii (bool): whether the files are in ascii.

            recursive (bool): whether to recursively store
                subdirectories.

        """
        basepath = os.path.abspath(basedir)
        filecontents = self.model.require_group('filecontents')
        for fname in filenames:
            fpath = os.path.abspath(fname)
            if not fpath.startswith(basepath):
                warnings.warn('{} does not start with basedir {}. Skipping.'.format(fname, basedir))
            if os.path.isfile(fname):
                buf = bytearray(os.path.getsize(fname))
                with open(fname, 'rb') as fhandle:
                    fhandle.readinto(buf)
                # Get the file path components in portable manner
                relative_path = fpath[len(basepath):]
                components = split_os_path(relative_path)
                if components[0] in ['/', '\\']:
                    components = components[1:]
                file_parent_path = '/'.join(components[:-1])
                if file_parent_path:
                    grp = filecontents.require_group(file_parent_path)
                else:
                    grp = filecontents
                if ascii:
                    fdata = write_ascii_file(grp, components[-1], fname, **self.h5args)
                else:
                    fdata = write_binary_file(grp, components[-1], fname, **self.h5args)
            elif os.path.isdir(fname):
                write_dir_contents(filecontents, fname, ascii=ascii, **self.h5args)
            else:
                warnings.warn('not a file or directory {}'.format(fname))

    def add_uniform_ds(self, name, idlist):

        """Add the sources listed in idlist under /map/uniform.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources.

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
        src_data = np.array(idlist, dtype=VLENSTR)
        src_ds = base.create_dataset(name, shape=(len(idlist),),
                                 dtype=VLENSTR, data=src_data)
        self._link_map_model(src_ds)
        return src_ds

    def add_nonuniform_ds(self, popname, idlist):
        """Add the sources listed in idlist under /map/nonuniform/{popname}.

        Args: 
            popname (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources. This becomes irrelevant if homogeneous=False.

        Returns:
            An HDF5 Dataset storing the source ids when dialect
            is VLEN or NANPADDED. This is converted into a dimension
            scale when actual data is added.

        Raises:
            AssertionError if idlist is empty or dialect is ONED.

        """
        base = None
        base = self.mapping.require_group(NONUNIFORM)
        assert self.dialect != dialect.ONED
        assert len(idlist) > 0
        src_data = np.array(idlist, dtype=VLENSTR)
        src_ds = base.create_dataset(popname, shape=(len(idlist),),
                                 dtype=VLENSTR, data=src_data)
        self._link_map_model(src_ds)
        return src_ds
    
    def add_nonuniform_ds_1d(self, popname, varname, idlist):
        """Add the sources listed in idlist under
        /map/nonuniform/{popname}/{varname}.

        In case of 1D datasets, for each variable we store the mapping
        from source id to dataset ref in a two column compund dataset
        with dtype=[('source', VLENSTR), ('data', REFTYPE)]

        Args: 
            popname (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.
            
            varname (str): name of the variable beind recorded. The
                same name should be passed when actual data is being
                added.
        
            idlist (list of str): list of unique identifiers of the
                data sources.

        Returns:
            An HDF5 Dataset storing the source ids in `source` column.

        Raises:
            AssertionError if idlist is empty or if dialect is not ONED.

        """
        base = self.mapping.require_group(NONUNIFORM)
        assert self.dialect == dialect.ONED, 'valid only for dialect=ONED'
        assert len(idlist) > 0, 'idlist must be nonempty'
        grp = base.require_group(popname)
        src_ds = grp.create_dataset(varname, shape=(len(idlist),),
                                dtype=SRCDATAMAPTYPE)
        for iii in range(len(idlist)):
            src_ds[iii] = (idlist[iii], None)
        self._link_map_model(src_ds)
        return src_ds

    def add_event_ds(self, name, idlist):
        """Create a group under `/map/event` with name `name` to store mapping
        between the datasources and event data.

        Args: 
            name (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list): unique ids of the data sources.

        Returns: 
            The HDF5 Group `/map/event/{name}`.

        """
        base = self.mapping.require_group(EVENT)
        assert len(idlist) > 0, 'idlist must be nonempty'
        assert ((self.dialect != dialect.ONED) and
                (self.dialect != dialect.NUREGULAR)),   \
            'only for VLEN or NANPADDED dialects'
        src_data = np.array(idlist, dtype=VLENSTR)
        src_ds = base.create_dataset(name, shape=(len(idlist),),
                                 data=src_data)
        self._link_map_model(src_ds)
        return src_ds

    def add_event_ds_1d(self, popname, varname, idlist):
        """Create a group under `/map/event` with name `name` to store mapping
        between the datasources and event data.

        Args: 
            popname (str): name of the group under which the
                datasource list should be stored. This will represent
                a population of data sources.

            varname (str): name of the dataset mapping source uid to
                data. This should be same as the name of the recorded
                variable.

        Returns: 
            The HDF5 Dataset `/map/event/{popname}/{varname}`.

        """
        base = self.mapping.require_group(EVENT)
        assert len(idlist) > 0, 'idlist must be nonempty'
        assert ((self.dialect == dialect.ONED) or
            (self.dialect == dialect.NUREGULAR)),   \
            'dialect must be ONED or NUREGULAR'
        grp = base.require_group(popname)
        src_ds = grp.create_dataset(varname, shape=(len(idlist),),
                                     dtype=SRCDATAMAPTYPE)
        for iii in range(len(idlist)):
            src_ds[iii] = (idlist[iii], None)
        self._link_map_model(src_ds)
        return src_ds

    def add_static_ds(self, popname, idlist):
        """Add the sources listed in idlist under /map/static.

        Args: 
            popname (str): name with which the datasource list
                should be stored. This will represent a population of
                data sources.

            idlist (list of str): list of unique identifiers of the
                data sources.

        Returns: 
            An HDF5 Dataset storing the source ids. This is
            converted into a dimension scale when actual data is
            added.

        """
        if len(idlist) == 0:
            raise ValueError('idlist must be nonempty')
        base = self.mapping.require_group(STATIC)
        # idlist = np.array(idlist, dtype=VLENSTR)
        src_ds = base.create_dataset(popname, shape=(len(idlist),),
                                 dtype=VLENSTR, data=idlist)
        self.modelroot.update_id_path_dict()
        self._link_map_model(src_ds)
        return src_ds        
    
    def add_uniform_data(self, source_ds, data_object, tstart=0.0,
                         fixed=False):
        """Append uniformly sampled `variable` values from `sources` to
        `data`.

        Args: 
            source_ds (HDF5 Dataset): the dataset storing the source
                ids under map. This is attached to the stored data as
                a dimension scale called `source` on the row
                dimension.

            data_object (nsdf.UniformData): Uniform dataset to be
                added to file.

            tstart (double): (optional) start time of this dataset
                recording. Defaults to 0.
            
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
        ugrp = self.data[UNIFORM].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match sources in'
                           ' `data`.')
        strinfo = h5.check_string_dtype(source_ds.dtype)
        if strinfo is not None:
            sources = [src.decode(strinfo.encoding) for src in source_ds]
        ordered_data = [data_object.get_data(src) for src in sources]
        data = np.vstack(ordered_data)
        try:
            dataset = ugrp[data_object.name]
            oldcolcount = dataset.shape[1]
            dataset.resize(oldcolcount + data.shape[1], axis=1)
            dataset[:, oldcolcount:] = data
        except KeyError:
            if data_object.dt <= 0.0:
                raise ValueError('`dt` must be > 0.0 for creating dataset.')
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            if data_object.tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            maxcol = None
            if fixed:
                maxcol = data.shape[1]
            dataset = ugrp.create_dataset(
                data_object.name,
                shape=data.shape,
                dtype=data_object.dtype,
                data=data,
                maxshape=(data.shape[0], maxcol),
                **self.h5args)
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'
            dataset.attrs['tstart'] = tstart
            dataset.attrs['dt'] = data_object.dt
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            dataset.attrs['tunit'] = data_object.tunit
        return dataset

    def add_nonuniform_regular(self, source_ds, data_object,
                               fixed=False):
        """Append nonuniformly sampled `variable` values from `sources` to
        `data`. In this case sampling times of all the sources are
        same and the data is stored in a 2D dataset.

        Args: 
            source_ds (HDF5 Dataset): the dataset storing the source
                ids under map. This is attached to the stored data as
                a dimension scale called `source` on the row
                dimension.
            
            data_object (nsdf.NonuniformRegularData):
                NonUniformRegular dataset to be added to file.

            fixed (bool): if True, the data cannot grow. Default: False

        Returns:
            HDF5 dataset storing the data

        Raises:
            KeyError if the sources in `data_object` do not match
            those in `source_ds`.
        
            ValueError if the data arrays are not all equal in length.

            ValueError if dt is not specified or <= 0 when inserting
            data for the first time.

        """
        popname = source_ds.name.rpartition('/')[-1]
        ngrp = self.data[NONUNIFORM].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match sources in'
                           ' `data_object`.')
        ordered_data = [data_object.get_data(src) for src in source_ds]
        data = np.vstack(ordered_data)
        if data.shape[1] != len(data_object.get_times()):
            raise ValueError('number sampling times must be '
                             'same as the number of data points')
        try:
            dataset = ngrp[data_object.name]
            oldcolcount = dataset.shape[1]
            dataset.resize(oldcolcount + data.shape[1], axis=1)
            dataset[:, oldcolcount:] = data
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            if data_object.tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            maxcol = None
            if fixed:
                maxcol = data.shape[1]
            dataset = ngrp.create_dataset(
                data_object.name, shape=data.shape,
                dtype=data.dtype,
                data=data,
                maxshape=(data.shape[0], maxcol),
                **self.h5args)
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            tsname = '{}_{}'.format(popname, data_object.name)
            tscale = self.time_dim.create_dataset(
                tsname,
                shape=(len(data_object.get_times()),),
                dtype=np.float64,
                data=data_object.get_times(),
                **self.h5args)
            tscale.make_scale('time')
            # dataset.dims.create_scale(tscale, 'time')
            dataset.dims[1].attach_scale(tscale)
            dataset.dims[1].label = 'time'
            tscale.attrs['unit'] = data_object.tunit
        return dataset

    def add_nonuniform_1d(self, source_ds, data_object,
                          source_name_dict=None, fixed=False):
        """Add nonuniform data when data from each source is in a separate 1D
        dataset.

        For a population of sources called {population}, a group
        `/map/nonuniform/{population}` must be first created (using
        add_nonuniform_ds). This is passed as `source_ds` argument.
        
        When adding the data, the uid of the sources and the names for
        the corresponding datasets must be specified and this function
        will create one dataset for each source under
        `/data/nonuniform/{population}/{name}` where {name} is the
        name of the data_object, preferably the name of the field
        being recorded.
        
        This function can be used when different sources in a
        population are sampled at different time points for a field
        value. Such case may arise when each member of the population
        is simulated using a variable timestep method like CVODE and
        this timestep is not global.

        Args: 
            source_ds (HDF5 dataset): the dataset
                `/map/nonuniform/{population}/{variable}` created for
                this population of sources (created by
                add_nonunifrom_ds_1d).

            data_object (nsdf.NonuniformData): NSDFData object storing
                the data for all sources in `source_ds`.

            source_name_dict (dict): mapping from source id to dataset
                name. If None (default), the uids of the sources will
                be used as dataset names. If the uids are not
                compatible with HDF5 names (contain '.' or '/'), then
                the index of the source in source_ds will be used.

            fixed (bool): if True, the data cannot grow. Default:
                False

        Returns:
            dict mapping source ids to the tuple (dataset, time).

        Raises:
            AssertionError when dialect is not ONED.

        """
        assert self.dialect == dialect.ONED, \
            'add 1D dataset under nonuniform only for dialect=ONED'
        if source_name_dict is None:
            names = np.array(source_ds['source'], dtype=np.str_)
            slash_pos = np.char.find(names, '/') 
            dot_pos = np.char.find(names, '.')
            if np.any(( slash_pos >= 0) |
                      ( dot_pos >= 0)):
                names = [str(index) for index in range(len(names))]
            source_name_dict = dict(list(zip(source_ds['source'], names)))

        assert len(set(source_name_dict.values())) == len(source_ds), \
            'The names in `source_name_dict` must be unique'        
        popname = source_ds.name.split('/')[-2]
        ngrp = self.data[NONUNIFORM].require_group(popname)
        assert match_datasets(list(source_name_dict.keys()),
                              data_object.get_sources()), \
               'sources in `source_name_dict`'    \
               ' do not match those in `data_object`'
        assert match_datasets(source_ds['source'],
                              list(source_name_dict.keys())),  \
            'sources in mapping dataset do not match those with data'
        datagrp = ngrp.require_group(data_object.name)
        datagrp.attrs['source'] = source_ds.ref
        datagrp.attrs['unit'] = data_object.unit
        datagrp.attrs['field'] = data_object.field
        ret = {}
        for iii, source in enumerate(source_ds['source']):
            data, time = data_object.get_data(source)
            dsetname = source_name_dict[source]
            timescale = None
            try:
                dset = datagrp[dsetname]
                oldlen = dset.shape[0]
                timescale = dset.dims[0]['time']
                dset.resize((oldlen + len(data),))
                dset[oldlen:] = data
                timescale.resize((oldlen + len(data),))
                timescale[oldlen:] = time
            except KeyError:
                if data_object.unit is None:
                    raise ValueError('`unit` is required'
                                     ' for creating dataset.')
                if data_object.tunit is None:
                    raise ValueError('`tunit` is required'
                                     ' for creating dataset.')
                maxcol = len(data) if fixed else None
                dset = datagrp.create_dataset(
                    dsetname,
                    shape=(len(data),),
                    dtype=data_object.dtype,
                    data=data,
                    maxshape=(maxcol,),
                    **self.h5args)
                dset.attrs['unit'] = data_object.unit
                dset.attrs['field'] = data_object.field
                dset.attrs['source'] = source
                source_ds[iii] = (source, dset.ref)
                # Using {popname}_{variablename}_{dsetname} for
                # simplicity. What about creating a hierarchy?
                tsname = '{}_{}_{}'.format(popname, data_object.name, dsetname)
                timescale = self.time_dim.create_dataset(
                    tsname,
                    shape=(len(data),),
                    dtype=data_object.ttype,
                    data=time,
                    maxshape=(maxcol,),
                    **self.h5args)
                # dset.dims.create_scale(timescale, 'time')
                timescale.make_scale('time')
                dset.dims[0].label = 'time'
                dset.dims[0].attach_scale(timescale)
                timescale.attrs['unit'] = data_object.tunit
            ret[source] = (dset, timescale)
        return ret
    
    def add_nonuniform_vlen(self, source_ds, data_object,
                                fixed=False):
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
            source_ds (HDF5 dataset): the dataset under
                `/map/nonuniform` created for this population of
                sources (created by add_nonunifrom_ds).

            data_object (nsdf.NonuniformData): NSDFData object storing
                the data for all sources in `source_ds`.

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

            h5py does not support vlen datasets with float64
            elements. Change dtype to np.float64 once that is
            developed.

        """
        if self.dialect != dialect.VLEN:
            raise Exception('add 2D vlen dataset under nonuniform'
                            ' only for dialect=VLEN')
        popname = source_ds.name.rpartition('/')[-1]
        ngrp = self.data[NONUNIFORM].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match keys of'
                           ' `source_data_dict`.')
        # Using {popname}_{variablename} for simplicity. What
        # about creating a hierarchy?
        tsname = '{}_{}'.format(popname, data_object.name)
        try:
            dataset = ngrp[data_object.name]
            time_ds = self.time_dim[tsname]
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            if data_object.tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            vlentype = h5.special_dtype(vlen=data_object.dtype)
            maxrows = source_ds.shape[0] if fixed else None
            # Fix me: is there any point of keeping the compression
            # and shuffle options?
            dataset = ngrp.create_dataset(
                data_object.name,
                shape=source_ds.shape,
                dtype=vlentype,
                **self.h5args)
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'
            # FIXME: VLENFLOAT should be made VLENDOUBLE whenever h5py
            # fixes it
            time_ds = self.time_dim.create_dataset(
                tsname,
                shape=dataset.shape,
                maxshape=(maxrows,),
                dtype=VLENFLOAT,
                **self.h5args)
            time_ds.make_scale('time')
            # dataset.dims.create_scale(time_ds, 'time')
            dataset.dims[0].attach_scale(time_ds)
            dataset.dims[0].label = 'time'            
            time_ds.attrs['unit'] = data_object.tunit
        for iii, source in enumerate(source_ds):
            data, time, = data_object.get_data(source)
            dataset[iii] = np.concatenate((dataset[iii], data))
            time_ds[iii] = np.concatenate((time_ds[iii], time))
        return dataset, time_ds

    def add_nonuniform_nan(self, source_ds, data_object, fixed=False):
        """Add nonuniform data when data from all sources in a population is
        stored in a 2D array with NaN padding.

        Args: 
            source_ds (HDF5 Dataset): the dataset under
                `/map/event` created for this population of
                sources (created by add_nonunifrom_ds).

            data_object (nsdf.EventData): NSDFData object storing
                the data for all sources in `source_ds`.

            fixed (bool): if True, this is a one-time write and the
                data cannot grow. Default: False

        Returns:
            HDF5 Dataset containing the data.

        Notes: 
            Concatenating old data with new data and reassigning is a
            poor choice for saving data incrementally. HDF5 does not
            seem to support appending data to VLEN datasets.

            h5py does not support vlen datasets with float64
            elements. Change dtype to np.float64 once that is
            developed.

        """
        assert self.dialect == dialect.NANPADDED,    \
            'add 2D dataset under `nonuniform` only for dialect=NANPADDED'
        popname = source_ds.name.rpartition('/')[-1]
        ngrp = self.data[NONUNIFORM].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match sources '
                           'in `data_object`.')
        # Using {popname}_{variablename} for simplicity. What
        # about creating a hierarchy?
        tsname = '{}_{}'.format(popname, data_object.name)
        cols = [len(data_object.get_data(source)[0]) for source in
                source_ds]
        starts = np.zeros(source_ds.shape[0], dtype=int)
        ends = np.asarray(cols, dtype=int)
        try:
            dataset = ngrp[data_object.name]
            for iii in range(source_ds.shape[0]):
                try:
                    starts[iii] = next(find(dataset[iii], np.isnan))[0][0]
                except StopIteration:
                    starts[iii] = len(dataset[iii])
                ends[iii] = starts[iii] + cols[iii]
            dataset.resize(max(ends), 1)            
            time_ds = self.time_dim[tsname]
            time_ds.resize(max(ends), 1)
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            if data_object.tunit is None:
                raise ValueError('`tunit` is required for creating dataset.')
            
            maxrows = len(source_ds) if fixed else None
            maxcols = max(cols) if fixed else None
            dataset = ngrp.create_dataset(
                data_object.name,
                shape=(source_ds.shape[0], max(ends)),
                maxshape=(maxrows, maxcols),
                fillvalue=np.nan,
                dtype=data_object.dtype,
                **self.h5args)
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'
            time_ds = self.time_dim.create_dataset(
                tsname,
                shape=dataset.shape,
                maxshape=(maxrows,maxcols),
                dtype=data_object.ttype,
                fillvalue=np.nan,
                **self.h5args)
            time_ds.make_scale('time')
            # dataset.dims.create_scale(time_ds, 'time')
            dataset.dims[1].attach_scale(time_ds)
            dataset.dims[1].label = 'time'            
            time_ds.attrs['unit'] = data_object.tunit
        for iii, source in enumerate(source_ds):
            data, time = data_object.get_data(source)
            dataset[iii, starts[iii]:ends[iii]] = data
            time_ds[iii, starts[iii]:ends[iii]] = time
        return dataset


    def add_event_1d(self, source_ds, data_object, source_name_dict=None,
                     fixed=False):
        """Add event time data when data from each source is in a separate 1D
        dataset.

        For a population of sources called {population}, a group
        `/map/event/{population}` must be first created (using
        add_event_ds). This is passed as `source_ds` argument.
        
        When adding the data, the uid of the sources and the names for
        the corresponding datasets must be specified in
        `source_name_dict` and this function will create one dataset
        for each source under `/data/event/{population}/{name}` where
        {name} is the name of the data_object, preferably the field
        name.
        
        Args: 
            source_ds (HDF5 Dataset): the dataset
                `/map/event/{populationname}{variablename}` created
                for this population of sources (created by
                add_event_ds_1d). The name of this group reflects
                that of the group under `/data/event` which stores the
                datasets.

            data_object (nsdf.EventData): NSDFData object storing
                the data for all sources in `source_ds`.

            source_name_dict (dict): mapping from source id to dataset
                name. If None (default) it tries to use the uids in
                the source_ds. If the uids do not fit the hdf5 naming
                convention, the index of the entries in source_ds will
                be used.

            fixed (bool): if True, the data cannot grow. Default:
                False

        Returns:
            dict mapping source ids to datasets.

        """
        assert ((self.dialect == dialect.ONED) or
            self.dialect == dialect.NUREGULAR), \
            'add 1D dataset under event only for dialect=ONED or NUREGULAR'
        strinfo = h5.check_string_dtype(source_ds['source'].dtype)
        if strinfo is None:
            sources = source_ds['source']
        else:
            sources = [src.decode(strinfo.encoding) for src in source_ds['source']]
        if source_name_dict is None:
            # if names contain invalid chars for HDF5 name, substitute with index
            if np.any((np.char.find(sources, '/') >= 0) |
                      (np.char.find(sources, '.') >= 0)):
                names = [str(index) for index in range(len(sources))]
            else:
                names = sources
            source_name_dict = dict(zip(sources, names))
        assert len(set(source_name_dict.values())) == len(source_ds), \
            'The names in `source_name_dict` must be unique'
        popname = source_ds.name.split('/')[-2]
        ngrp = self.data[EVENT].require_group(popname)
        assert match_datasets(source_name_dict.keys(),
                              data_object.get_sources()),  \
            'sources do not match dataset'
        datagrp = ngrp.require_group(data_object.name)
        datagrp.attrs['source'] = source_ds.ref
        datagrp.attrs['unit'] = data_object.unit
        datagrp.attrs['field'] = data_object.field
        ret = {}
        for iii, source in enumerate(sources):
            data = data_object.get_data(source)
            dsetname = source_name_dict[source]
            try:
                dset = datagrp[dsetname]
                oldlen = dset.shape[0]
                dset.resize((oldlen + len(data),))
                dset[oldlen:] = data
            except KeyError:
                if data_object.unit is None:
                    raise ValueError('`unit` is required for creating dataset.')
                if data_object.field is None:
                    raise ValueError('`field` is required for creating dataset.')
                maxrows = len(data) if fixed else None
                dset = datagrp.create_dataset(
                    dsetname,
                    shape=(len(data),),
                    dtype=data_object.dtype, data=data,
                    maxshape=(maxrows,),
                    **self.h5args)
                dset.attrs['unit'] = data_object.unit
                dset.attrs['field'] = data_object.field
                dset.attrs['source'] = source
                source_ds[iii] = (source, dset.ref)
            ret[source] = dset
        return ret
    
    def add_event_vlen(self, source_ds, data_object, fixed=False):
        """Add event data when data from all sources in a population is
        stored in a 2D ragged array.

        When adding the data, the uid of the sources and the names for
        the corresponding datasets must be specified and this function
        will create the dataset `/data/event/{population}/{name}`
        where {name} is name of the data_object, preferably the name
        of the field being recorded.
        
        Args: 
            source_ds (HDF5 Dataset): the dataset under
                `/map/event` created for this population of
                sources (created by add_nonunifrom_ds).

            data_object (nsdf.EventData): NSDFData object storing
                the data for all sources in `source_ds`.

            fixed (bool): if True, this is a one-time write and the
                data cannot grow. Default: False

        Returns:
            HDF5 Dataset containing the data.

        Notes: 
            Concatenating old data with new data and reassigning is a
            poor choice for saving data incrementally. HDF5 does not
            seem to support appending data to VLEN datasets.

            h5py does not support vlen datasets with float64
            elements. Change dtype to np.float64 once that is
            developed.

        """
        if self.dialect != dialect.VLEN:
            raise Exception('add 2D vlen dataset under event'
                            ' only for dialect=VLEN')
        popname = source_ds.name.rpartition('/')[-1]
        ngrp = self.data[EVENT].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match sources '
                           'in `data_object`.')        
        try:
            dataset = ngrp[data_object.name]
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            vlentype = h5.special_dtype(vlen=data_object.dtype)
            maxrows = len(source_ds) if fixed else None
            # Fix me: is there any point of keeping the compression
            # and shuffle options?
            dataset = ngrp.create_dataset(
                data_object.name, shape=source_ds.shape,
                maxshape=(maxrows,),
                dtype=vlentype,
                **self.h5args)
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'            
        for iii, source in enumerate(source_ds):
            data = data_object.get_data(source)
            dataset[iii] = np.concatenate((dataset[iii], data))
        return dataset

    def add_event_nan(self, source_ds, data_object, fixed=False):
        """Add event data when data from all sources in a population is
        stored in a 2D array with NaN padding.

        Args: 
            source_ds (HDF5 Dataset): the dataset under
                `/map/event` created for this population of
                sources (created by add_nonunifrom_ds).

            data_object (nsdf.EventData): NSDFData object storing
                the data for all sources in `source_ds`.

            fixed (bool): if True, this is a one-time write and the
                data cannot grow. Default: False

        Returns:
            HDF5 Dataset containing the data.

        """
        assert self.dialect == dialect.NANPADDED,    \
            'add 2D vlen dataset under event only for dialect=NANPADDED'
        popname = source_ds.name.rpartition('/')[-1]
        ngrp = self.data[EVENT].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match sources '
                           'in `data_object`.')
        cols = [len(data_object.get_data(source)) for source in
                source_ds]
        starts = np.zeros(source_ds.shape[0], dtype=int)
        ends = np.asarray(cols, dtype=int)
        try:
            dataset = ngrp[data_object.name]
            for iii in range(dataset.shape[0]):
                try:
                    starts[iii] = next(find(dataset[iii], np.isnan))[0][0]
                except StopIteration:
                    starts[iii] = len(dataset[iii])
                ends[iii] = starts[iii] + cols[iii]
            dataset.resize(max(ends), 1)            
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            maxrows = len(source_ds) if fixed else None
            maxcols = max(ends) if fixed else None
            dataset = ngrp.create_dataset(
                data_object.name,
                shape=(source_ds.shape[0], max(ends)),
                maxshape=(maxrows, maxcols),
                dtype=data_object.dtype,
                fillvalue=np.nan,
                **self.h5args)
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'            
        for iii, source in enumerate(source_ds):
            data = data_object.get_data(source)
            dataset[iii, starts[iii]:ends[iii]] = data
        return dataset
    
    def add_static_data(self, source_ds, data_object,
                        fixed=True):
        """Append static data `variable` values from `sources` to `data`.

        Args: 
           source_ds (HDF5 Dataset): the dataset storing the source
                ids under map. This is attached to the stored data as
                a dimension scale called `source` on the row
                dimension.

            data_object (nsdf.StaticData): NSDFData object storing
                the data for all sources in `source_ds`.
            
            fixed (bool): if True, the data cannot grow. Default: True

        Returns:
            HDF5 dataset storing the data

        Raises:
            KeyError if the sources in `source_data_dict` do not match
            those in `source_ds`.
        
        """
        popname = source_ds.name.rpartition('/')[-1]
        strinfo = h5.check_string_dtype(source_ds.dtype)
        # This is to handle  h5py VLEN str presented as bytes
        # conflicting with python str
        if strinfo is not None:
            src_ds_ = [src.decode(strinfo.encoding) for src in source_ds]
        else:
            src_ds_ = src_ds
        ugrp = self.data[STATIC].require_group(popname)
        if not match_datasets(source_ds, data_object.get_sources()):
            raise KeyError('members of `source_ds` must match keys of'
                           ' `source_data_dict`.')
        ordered_data = [data_object.get_data( src) for src in    \
                        src_ds_]
        data = np.vstack(ordered_data)
        try:
            dataset = ugrp[data_object.name]
            oldcolcount = dataset.shape[1]
            dataset.resize(oldcolcount + data.shape[1], axis=1)
            dataset[:, oldcolcount:] = data
        except KeyError:
            if data_object.unit is None:
                raise ValueError('`unit` is required for creating dataset.')
            maxcol = None
            if fixed:
                maxcol = data.shape[1]
            dataset = ugrp.create_dataset(
                data_object.name, shape=data.shape,
                dtype=data_object.dtype,
                data=data,
                maxshape=(data.shape[0], maxcol),
                **self.h5args)
            source_ds.make_scale('source')
            dataset.dims[0].attach_scale(source_ds)
            dataset.dims[0].label = 'source'                        
            dataset.attrs['field'] = data_object.field
            dataset.attrs['unit'] = data_object.unit
        return dataset

    
# 
# nsdfwriter.py ends here
