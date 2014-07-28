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
        




# 
# util.py ends here
