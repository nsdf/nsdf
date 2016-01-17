# util.py --- 
# 
# Filename: util.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Jul 28 15:13:33 2014 (+0530)
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
"""Utility functions for nsdf."""
from __future__ import print_function
from builtins import zip
from builtins import range

__author__ = 'Subhasis Ray'

import numpy as np
from itertools import chain
import h5py as h5

def node_finder(container_list, match_fn):
    """Return a function that can be passed to h5py.Group.visititem to
    collect all nodes satisfying `match_fn` collect in `container_list`"""
    def collector(name, obj):
        """Collect all nodes returning True for match_fn"""
        if match_fn(obj):
            container_list.append(obj)
        return None
    return collector
        


# The following was taken from numpy issue tracker. Originally
# submitted by Phil Elson. This is a workaround for find_first until
# numpy2.0 comes out with an implementation of the same.
# Subhasis Ray, Wed Jul 30 11:27:23 IST 2014


def find(a, predicate, chunk_size=1024):
    """Find the indices of array elements that match the predicate.

    Parameters
    ----------
    a : array_like
        Input data, must be 1D.

    predicate : function
        A function which operates on sections of the given array, returning
        element-wise True or False for each data value.

    chunk_size : integer
        The length of the chunks to use when searching for matching indices.
        For high probability predicates, a smaller number will make this
        function quicker, similarly choose a larger number for low
        probabilities.

    Returns
    -------
    index_generator : generator
        A generator of (indices, data value) tuples which make the predicate
        True.

    See Also
    --------
    where, nonzero

    Notes
    -----
    This function is best used for finding the first, or first few, data values
    which match the predicate.

    Examples
    --------
    >>> a = np.sin(np.linspace(0, np.pi, 200))
    >>> result = find(a, lambda arr: arr > 0.9)
    >>> next(result)
    ((71, ), 0.900479032457)
    >>> np.where(a > 0.9)[0][0]
    71

    Author:

        Phil Elson (https://github.com/pelson). Code taken from numpy
        issue tracker: https://github.com/numpy/numpy/issues/2269# on
        Wed Jul 30 11:20:23 IST 2014

    """
    if a.ndim != 1:
        raise ValueError('The array must be 1D, not {}.'.format(a.ndim))

    i0 = 0
    chunk_inds = chain(range(chunk_size, a.size, chunk_size), 
                 [None])

    for i1 in chunk_inds:
        chunk = a[i0:i1]
        for inds in zip(*predicate(chunk).nonzero()):
            yield (inds[0] + i0, ), chunk[inds]
        i0 = i1

        
def printtree(root, vchar='|', hchar='__', vcount=1, depth=0, prefix='', is_last=False):
    """Pretty-print an HDF5 tree.
    
    Parameters
    ----------
    root : h5py.Group
        path of the root element of the HDF5 subtree to be printed.

    vchar : str 
        the character printed to indicate vertical continuation of
        a parent child relationship.

    hchar : str
        the character printed just before the node name.

    vcount : int
        determines how many lines will be printed between two
        successive nodes.

    depth : int
        for internal use - should not be explicitly passed.

    prefix : str
        for internal use - should not be explicitly passed.

    is_last : bool
        for internal use - should not be explicitly passed.

    """
    for i in range(vcount):
        print(prefix)

    if depth != 0:
        print(prefix + hchar, end='')
        if is_last: # Special formatting for last child
            index = prefix.rfind(vchar)
            prefix = prefix[:index] + ' ' * (len(hchar) + len(vchar)) + vchar
        else:
            prefix = prefix + ' ' * len(hchar) + vchar
    else:
        prefix = prefix + vchar

    if isinstance(root, h5.File):
        print(root.name)
    else:
        print(root.name.rpartition('/')[-1])
    if not isinstance(root, h5.Group):
        return
    children = list(root.keys())
    for child in children[:-1]:        
        printtree(root[child], vchar, hchar, vcount, depth+1, prefix, False)
    # Need special formatting for the last child - no further vertical line
    if len(children) > 0:
        printtree(root[children[-1]], vchar, hchar, vcount, depth + 1, prefix, True)
        

# 
# util.py ends here
