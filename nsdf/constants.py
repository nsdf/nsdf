# constants.py --- 
# 
# Filename: constants.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Jul 21 16:20:00 2014 (+0530)
# Version: 
# Last-Updated: Tue Apr  9 18:56:53 2024 (+0530)
#           By: Subhasis Ray
#     Update #: 1
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
# from collections import namedtuple

VLENFLOAT = h5.special_dtype(vlen=np.dtype('float32'))
VLENDOUBLE = h5.special_dtype(vlen=np.dtype('float64'))
# VLENSTR = h5.special_dtype(vlen=str)  # h5py 2
VLENSTR = h5.string_dtype(encoding='utf-8')  # newer h5py
REFTYPE = h5.special_dtype(ref=h5.Reference)
VLENBYTE = h5.special_dtype(vlen=bytes)
SRCDATAMAPTYPE = np.dtype([('source', VLENSTR), ('data', REFTYPE)])

# NonuniformRec = namedtuple('NonuniformRec', ['sid', 'data', 'time'])

UNIFORM = 'uniform'
NONUNIFORM = 'nonuniform'
EVENT ='event'
STATIC = 'static'

# Enums for dialects
class dialect(object):
    """Enumeration of different dialects of NSDF. 

    The following constants are defined:
    
    
        VLEN: 
            nonuniform and event data stored in vlen 2d datasets.
    
        ONED: 
            nonuniform and event data stored in 1d datasets.
         
        NANPADDED: 
            nonuniform and event data stored in regular 2d datasets
            with NaN padding.
    
        NUREGULAR: 
            nonuniform datasets have shared sampling times. Thus
            nonuniform data goes into regular 2D datasets. In this case
            the events are stored in 1D datasets.

    """
    VLEN = 'VLEN'
    ONED = 'ONED'   
    NANPADDED = 'NANPADDED'      
    NUREGULAR = 'NUREGULAR'

    
SAMPLING_TYPES = [UNIFORM, NONUNIFORM, EVENT, STATIC]




# 
# constants.py ends here
