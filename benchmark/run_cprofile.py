# run_cprofile.py --- 
# 
# Filename: run_cprofile.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Thu Sep  4 15:05:32 2014 (+0530)
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
"""Script to run cProfile on the benchmark writer"""
import os
import sys
import pstats
import socket
import subprocess
from datetime import datetime

mincol = 5000
maxcol = 15000
nvar = 100
sources = 100
hostname = socket.gethostname()
pid = os.getpid()
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

if __name__ == '__main__':
    for sampling in ['uniform', 'nonuniform', 'event']:
        for dialect in ['oned', 'nan', 'vlen']:
            for compression in ['', '-c']:
                for increment in [0, 1000]:
                    outfile = '{}_{}_{}_{}_{}_{}_{}.prof'.format(
                        dialect, sampling,
                        'fixed' if increment == 0 else 'incr',
                        'uncompressed' if not compression else 'compressed',
                        hostname, pid, timestamp)
                    args = ['python', '-m', 'cProfile', '-o', outfile,
                            'benchmark_writer.py', '-i', str(increment), '-s', sampling,
                            '-m', str(mincol), '-n', str(maxcol), '-d',
                            str(dialect), '-v', str(nvar), '-x',
                            str(sources), '-o', outfile.replace('prof', 'h5')]
                    if compression:
                        args.append(compression)
                    subprocess.call(args)
                    stats = pstats.Stats(outfile).strip_dirs().sort_stats('name')
                    print 'dialect', 'increment', 'compression'
                    stats.print_stats('nsdfwriter.*add_')
                    stats.print_stats('benchmark_writer.*write_')
                    print 


# 
# run_cprofile.py ends here
