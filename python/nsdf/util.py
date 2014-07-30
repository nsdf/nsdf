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
__author__ = 'Subhasis Ray'

def node_finder(container_list, match_fn):
    """Return a function that can be passed to h5py.Group.visititem to
    collect all nodes satisfying `match_fn` collect in `container_list`"""
    def collector(name, obj):
        """Collect all nodes returning True for match_fn"""
        if match_fn(obj):
            container_list.append(obj)
        return None
    return collector
        

import numpy as np
from itertools import chain, izip

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
    chunk_inds = chain(xrange(chunk_size, a.size, chunk_size), 
                 [None])

    for i1 in chunk_inds:
        chunk = a[i0:i1]
        for inds in izip(*predicate(chunk).nonzero()):
            yield (inds[0] + i0, ), chunk[inds]
        i0 = i1


# 
# util.py ends here
