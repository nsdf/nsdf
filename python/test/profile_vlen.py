# profile_nan.py --- 
# 
# Filename: profile_nan.py
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
"""Profile the NaN filled 2D homogeneous array case."""

import os
import sys
import subprocess
import random

sourcefile = '/data/subha/rsync_ghevar_cortical_data_clone/2012_05_22/data_20120522_152734_10973.h5'
targetfilebase = os.path.basename(sourcefile)
repeats = 10

# I have NaN in a separate branch - for a rough profile I am not
# worrying about the sequence of execution between NaN and orther
# variations
if __name__ == '__main__':
    seq = range(4 * repeats)
    random.shuffle(seq)
    for ii in seq:
        if ii < 10:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'uncompressed_%d.prof' % (ii), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_uncompressed_%d_%s' % (ii, targetfilebase)), 'False', 'False'])
        elif ii < 20:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'compressed_%d.prof' % (ii-10), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_compressed_%d_%s' % (ii-10, targetfilebase)), 'False', 'True'])
        elif ii < 30:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'vlen_compressed_%d.prof' % (ii-10), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_compressed_%d_%s' % (ii-10, targetfilebase)), 'True', 'True'])
        else:
            subprocess.call(['python', '-m', 'cProfile', '-o', 'vlen_compressed_%d.prof' % (ii-10), 'test_nsdfwriter.py', sourcefile, os.path.join('/data', 'subha', 'tmp', 'nan_compressed_%d_%s' % (ii-10, targetfilebase)), 'True', 'True'])



# 
# profile_nan.py ends here
