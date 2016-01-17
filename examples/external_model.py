# external_model.py --- 
# 
# Filename: external_model.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Aug  4 12:43:07 2014 (+0530)
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
"""An example of 'External Link' in HDF5 to connect external HDF5 file
as model description."""
from __future__ import print_function

import numpy as np
import h5py as h5

def create_demo():
    """This is just to show that the data is not stored in the main file,
    as the size of external.h5 is much bigger than main.h5.

    """
    external = h5.File('external.h5', 'w')
    nrn = external.create_group('neuron')
    comp = nrn.create_group('soma')
    comp['data'] = np.random.uniform(0, 1, size=1000000)
    external.close()

    main = h5.File('main.h5', 'w')
    model = main.create_group('model')
    links = model.create_group('links')
    links['neuron'] = h5.ExternalLink('external.h5', '/neuron')
    main.close()    

def printx(name):
    """Interestingly printx does not print the external nodes."""
    print(name)

def printy(name, obj):
    """Interestingly printx does not print the external nodes."""
    print('###', name)
    for ii in obj:
        print('#    ', ii, obj[ii], type(obj[ii]))

if __name__ == '__main__':
    create_demo()
    with h5.File('main.h5', 'r') as fd:
        fd.visit(printx)
        fd.visititems(printy)
        
    
    



# 
# external_model.py ends here
