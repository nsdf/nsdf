# profile_writing_dialects.py.py --- 
# 
# Filename: profile_writing_dialects.py.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon May 26 22:17:16 2014 (+0530)
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
"""Profile the different dialects of NaN filled 2D homogeneous array, vlen and 1D cases."""
from builtins import range

import os
import sys
import subprocess
import random

sourcefile = '/data/subha/rsync_ghevar_cortical_data_clone/2012_05_22/data_20120522_152734_10973.h5'
targetfilebase = os.path.basename(sourcefile)
repeats = 10

if __name__ == '__main__':
    seq = list(range(6 * repeats))
    random.shuffle(seq)
    for ii in seq:
        if ii < 10:
            subprocess.call(['python', '-m', 'cProfile', '-o', '1d_uncompressed_%d.prof' % (ii), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', '1d_uncompressed_%d_%s' % (ii, targetfilebase)), '1d', 'False'])
        elif ii < 20:
            subprocess.call(['python', '-m', 'cProfile', '-o', '1d_compressed_%d.prof' % (ii-10), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', '1d_compressed_%d_%s' % (ii-10, targetfilebase)), '1d', 'True'])
        elif ii < 30:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'vlen_uncompressed_%d.prof' % (ii-20), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'vlen_uncompressed_%d_%s' % (ii-20, targetfilebase)), 'vlen', 'False'])
        elif ii < 40:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'vlen_compressed_%d.prof' % (ii-30), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'vlen_compressed_%d_%s' % (ii-30, targetfilebase)), 'vlen', 'True'])
        elif ii < 50:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'nan_uncompressed_%d.prof' % (ii-40), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_uncompressed_%d_%s' % (ii-30, targetfilebase)), 'nan', 'False'])
        else:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'nan_compressed_%d.prof' % (ii-50), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_compressed_%d_%s' % (ii-30, targetfilebase)), 'nan', 'True'])



# 
# profile_writing_dialects.py.py ends here
