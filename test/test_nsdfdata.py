# test_nsdfdata.py --- 
# 
# Filename: test_nsdfdata.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Tue Jul 29 15:30:20 2014 (+0530)
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
"""Unit tests NSDFData subclasses."""

import sys
from collections import defaultdict
import numpy as np
from numpy import testing as nptest
import h5py as h5
from datetime import datetime
import unittest
import os

sys.path.append('..')
import nsdf

from util import *

class TestNSDFUniformData(unittest.TestCase):
    def setUp(self):
        self.data = nsdf.UniformData('test', unit='m', field='distance')
        
    def test_create(self):
        self.assertEqual(self.data.name, 'test')
        self.assertEqual(self.data.unit, 'm')
        self.assertEqual(self.data.field, 'distance')

    def test_put(self):
        src_data_dict = {'src_{}'.format(name): np.random.uniform(1000)
                         for name in 'abc'}
        for name, data in src_data_dict.items():
            self.data.put_data(name, data)
        self.assertEqual(len(src_data_dict), self.data.get_sources())
        self.assertEqual(set(src_data_dict.keys()),
                         set(self.data.get_sources()))

    def test_set_dt(self):
        self.data.set_dt(1.0, 's')
        self.assertEqual(self.data.dt, 1.0)
        self.assertEqual(self.data.tunit, 's')


# 
# test_nsdfdata.py ends here
