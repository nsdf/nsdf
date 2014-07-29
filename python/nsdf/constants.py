# constants.py --- 
# 
# Filename: constants.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Jul 21 16:20:00 2014 (+0530)
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
# Floor, Boston, MA 02110-1301, USA.VLENSTR = h5.special_dtype(vlen=str)

# 
# 

# Code:

import h5py as h5
import numpy as np
# from collections import namedtuple

VLENFLOAT = h5.special_dtype(vlen=np.dtype('float32'))
VLENDOUBLE = h5.special_dtype(vlen=np.dtype('float64'))
VLENSTR = h5.special_dtype(vlen=str)
REFTYPE = h5.special_dtype(ref=h5.Reference)
SRCDATAMAPTYPE = np.dtype([('source', VLENSTR), ('data', REFTYPE)])

# NonuniformRec = namedtuple('NonuniformRec', ['sid', 'data', 'time'])

UNIFORM = 'uniform'
NONUNIFORM = 'nonuniform'
EVENT ='event'
STATIC = 'static'

# Enums for dialects
class dialect(object):
    """Enumeration of different dialects of NSDF.

    VLEN: nonuniform and event data are in vlen 2d datasets

    ONED: nonuniform and event data are in 1d datasets
     
    NANFILLED: nonuniform and event data in regular 2d
    datasets with NaN padding in extra entrie

    NUREGULAR: nonuniform data has shared sampling times. Thus
    nonuniform data goes into regular 2D datasets.  In this case the
    events are stored in 1D datasets.

    """
    VLEN = 0    
    ONED = 1   
    NANFILLED = 2      
    NUREGULAR = 3

SAMPLING_TYPES = [UNIFORM, NONUNIFORM, EVENT, STATIC]




# 
# constants.py ends here
