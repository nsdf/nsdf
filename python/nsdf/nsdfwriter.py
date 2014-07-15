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

from model import ModelComponent

VLENSTR = h5.special_dtype(vlen=str)
VLENFLOAT = h5.special_dtype(vlen='float32')

SAMPLING_TYPES = ['uniform', 'nonuniform', 'event', 'static']

class NSDFWriter(object):
    """Writer for NSDF files.

    An NSDF file has three main groups: `/model`, `/data` and `/map`.

    """    
    def __init__(self, filename):
        self._fd = h5.File(filename, 'w')
        self.data = self._fd.create_group('/data')
        self.model = self._fd.create_group('/model')
        self.mapping = self._fd.create_group('/map')
        for stype in SAMPLING_TYPES:
            self.data.create_group(stype)
            self.mapping.create_group(stype)
        self.time_dim = self.mapping.create_group('time')
        self._modeltree_grp = self.model.create_group('modeltree')
        self.modelroot = ModelComponent('modeltree', uid='/model/modeltree',
                                        hdfgroup = self._modeltree_grp)

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
        
    def add_data_sources(self, population, path_id_dict, sampletype):
        """Add the sources listed in path_id_dict under map.

        Args: 
            population (str): name with which the datasource list
                should be stored. This will represent a population of data
                sources.

            path_id_dict (dict): maps the path of the source in
                model tree to the unique id of the source.

            sampletype (str): one of `uniform`, `nonuniform` and
                `event`.

        Returns: 
            An HDF5 Dataset storing the source ids. This is
            convrted into a dimension scale.

        """
        pass

    def add_uniform_data(self, variable, sources, id_data_dict):
        """Append uniformly sampled `variable` values from `sources` to
        `data`.

        Args: 
            variable (str): name of the recorded variable. The Dataset
                will have the same name.

            sources (HDF5 Dataset): the dataset storing the source ids
                under map.

            id_data_dict (dict): a dict mapping source ids to data
                arrays. The data arrays are numpy arrays.

        """
        pass
    

# 
# nsdfwriter.py ends here
