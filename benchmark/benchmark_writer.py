# benchmark_writer.py --- 
# 
# Filename: benchmark_writer.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Wed Sep  3 10:22:50 2014 (+0530)
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
"""This script benchmarks the nsdf writer using randomly generated
data.

Note that we violate the unique source id requirement here.

"""

import sys
import argparse
from collections import defaultdict
import numpy as np
from numpy import testing as nptest
import h5py as h5
from datetime import datetime
import unittest
import os
import socket

sys.path.append('..')
import nsdf

DATADIR = '/data/subha/nsdf_samples/benchmark'
HOSTNAME = socket.gethostname()
PID = os.getpid()
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

np.random.seed(1) # For reproducibility

def get_poisson_times(npoints, rate):
    """Return `npoints` time points from a Poisson event with rate
    `rate`"""
    scale = 1.0/rate
    return np.cumsum(np.random.exponential(scale=scale, size=npoints))


def create_uniform_data(name, num_sources, num_cols):
    """Create data for m=`num_sources`, each n=`num_cols` long."""
    data = nsdf.UniformData(name, field='Vm', unit='V', dt=1e-5, tunit='s', dtype=np.float32)
    for ii in range(num_sources):
        data.put_data('src_{}'.format(ii), np.random.rand(num_cols))
    return data


def create_nonuniform_data(name, num_sources, mincol, maxcol):
    """Create nonuniform data for m=`num_sources`, the number of sampling
    points n for each source is randomly chosen between `mincol` and
    `maxcol`

    """
    data = nsdf.NonuniformData(name, unit='V', tunit='s', dtype=np.float32, ttype=np.float32)
    if mincol < maxcol:
        ncols = np.random.randint(low=mincol, high=maxcol, size=num_sources)
    else:
        ncols = np.ones(num_sources, dtype=int) * maxcols
    for ii in range(num_sources):
        value = np.random.rand(ncols[ii])
        time = get_poisson_times(ncols[ii], 10)
        data.put_data('src_{}'.format(ii), (value, time))
    return data


def create_event_data(name, num_sources, mincol, maxcol):
    """Create event data for m=`num_sources`, the number of sampling
    points for each source is randomly chosen between `mincol` and
    `maxcol`

    """
    data = nsdf.EventData(name, unit='s', dtype=np.float32)
    ncols = np.random.randint(low=mincol, high=maxcol, size=num_sources)
    for ii in range(num_sources):
        data.put_data('src_{}'.format(ii), get_poisson_times(ncols[ii], 10))
    return data


def create_uniform_vars(num_vars, num_sources, num_cols, prefix='var'):
    """Note that they all share the same sources."""
    ret = []
    for ii in range(num_vars):
        ret.append(create_uniform_data('{}_{}'.format(prefix, ii),
                                       num_sources,
                                       num_cols))
    return ret


def create_nonuniform_vars(num_vars, num_sources, mincol, maxcol, prefix='var'):
    """Note that they all share the same sources."""
    ret = []
    for ii in range(num_vars):
        ret.append(create_nonuniform_data('{}_{}'.format(prefix, ii),
                                          num_sources,
                                          mincol, maxcol))
    return ret


def create_event_vars(num_vars, num_sources, mincol, maxcol, prefix='var'):
    """Note that they all share the same sources."""
    ret = []
    for ii in range(num_vars):
        ret.append(create_event_data('{}_{}'.format(prefix, ii),
                                     num_sources, mincol, maxcol))
    return ret


def create_datasets(args):
    uvar_list = []
    nvar_list = []
    evar_list = []
    
    if args.sampling:
        if args.sampling.startswith('u'):
            uvar_list = create_uniform_vars(args.variables,
                                            args.sources,
                                            (args.maxcol + args.mincol) / 2,
                                            prefix='uniform')
        elif args.sampling.startswith('n'):
            nvar_list = create_nonuniform_vars(args.variables,
                                               args.sources,
                                               args.mincol,
                                               args.maxcol,
                                               prefix='nonuniform')
        elif args.sampling.startswith('e'):
            evar_list = create_event_vars(args.variables,
                                          args.sources,
                                          args.mincol,
                                          args.maxcol,
                                          prefix='event')

    else:
        uvar_list = create_uniform_vars(args.variables,
                                        args.sources,
                                        (args.maxcol + args.mincol) / 2,
                                        prefix='uniform')
        nvar_list = create_nonuniform_vars(args.variables,
                                           args.sources,
                                           args.mincol,
                                           args.maxcol,
                                           prefix='nonuniform')
        evar_list = create_event_vars(args.variables,
                                      args.sources,
                                      args.mincol,
                                      args.maxcol,
                                      prefix='event')

    return {'uniform': uvar_list,
            'nonuniform': nvar_list,
            'event': evar_list}

def write_incremental(writer, source_ds, data, step, maxcol, dialect):
    for ii in range(0, maxcol + step - 1, step):
        if isinstance(data, nsdf.UniformData):
            tmp = nsdf.UniformData(data.name, unit=data.unit,
                                   dt=data.dt, tunit=data.tunit, dtype=np.float32)
            for src, value in data.get_source_data_dict().items():
                tmp.put_data(src, value[ii: ii + step])
            writer.add_uniform_data(source_ds, tmp)
        elif isinstance(data, nsdf.NonuniformData):
            tmp = nsdf.NonuniformData(data.name, unit=data.unit,
                                      tunit=data.tunit, dtype=np.float32, ttype=np.float32)
            for src, (value, time) in data.get_source_data_dict().items():
                value_chunk = value[ii: ii+step]
                time_chunk = time[ii: ii+step]
                tmp.put_data(src, (value_chunk, time_chunk))
            if dialect == nsdf.dialect.ONED:
                writer.add_nonuniform_1d(source_ds, tmp)
            elif dialect == nsdf.dialect.VLEN:
                writer.add_nonuniform_vlen(source_ds, tmp)
            else:
                writer.add_nonuniform_nan(source_ds, tmp)
        elif isinstance(data, nsdf.EventData):
            tmp = nsdf.EventData(data.name, unit=data.unit, dtype=np.float32)
            for src, value in data.get_source_data_dict().items():
                value_chunk = value[ii: ii+step]
                tmp.put_data(src, value_chunk)
            if dialect == nsdf.dialect.ONED:
                writer.add_event_1d(source_ds, tmp)
            elif dialect == nsdf.dialect.VLEN:
                writer.add_event_vlen(source_ds, tmp)
            else:
                writer.add_event_nan(source_ds, tmp)
                
            
def write_data(args, var_dict):
    """Write data from `var_dict` to benchmark files.

    file names are of the form:
    
    benchmark_out_{dialect}_{incremental}_{compression}.h5

    where dialect is oned, vlen or nan,
    incremental is incr of fixed,
    compression is compressed or uncompressed.
    """
    if args.dialect == 'vlen':
        dialect = nsdf.dialect.VLEN
    elif args.dialect == 'nan':
        dialect = nsdf.dialect.NANPADDED
    else:
        dialect = nsdf.dialect.ONED
    filename = args.out
    if not filename:
        filename = 'benchmark_out_{0}_{1}_{2}_{3}_{4}_{5}_{6}.h5'.format(
            dialect, args.sampling,
            'incr' if (args.increment > 0) else 'fixed',
            'compressed' if args.compress else 'uncompressed',
            HOSTNAME,
            PID, TIMESTAMP)
    filepath = os.path.join(DATADIR, filename)
                  
    if args.compress:
        writer = nsdf.NSDFWriter(filepath, dialect=dialect, mode='w',
                                 compression='gzip',
                                 compression_opts=6, fletcher32=True,
                                 shuffle=True)
    else:
        writer = nsdf.NSDFWriter(filepath, dialect=dialect,
                                 mode='w')

    uvar_list = var_dict.get('uniform', [])                                 
    for uvar in uvar_list:
        source_ds = writer.add_uniform_ds(uvar.name, uvar.get_sources())
        if args.increment <= 0:
            writer.add_uniform_data(source_ds, uvar, fixed=True)
        else:
            write_incremental(writer, source_ds, uvar,
                              args.increment, args.maxcol,
                              dialect)
    nuvar_list = var_dict.get('nonuniform', [])
    for nuvar in nuvar_list:
        if dialect == nsdf.dialect.ONED:
            source_ds = writer.add_nonuniform_ds_1d(nuvar.name,
                                                    nuvar.name,
                                                    nuvar.get_sources())
        else:
            source_ds = writer.add_nonuniform_ds(nuvar.name,
                                                 nuvar.get_sources())
        if args.increment <= 0:
            if dialect == nsdf.dialect.ONED:
                writer.add_nonuniform_1d(source_ds, nuvar, fixed=True)
            elif dialect == nsdf.dialect.VLEN:
                writer.add_nonuniform_vlen(source_ds, nuvar, fixed=True)
            if dialect == nsdf.dialect.NANPADDED:
                writer.add_nonuniform_nan(source_ds, nuvar, fixed=True)
        else:
            write_incremental(writer, source_ds, nuvar,
                              args.increment, args.maxcol,
                              dialect)
    evar_list = var_dict.get('event', [])
    for evar in evar_list:
        if dialect == nsdf.dialect.ONED:
            source_ds = writer.add_event_ds_1d(evar.name,
                                                    evar.name,
                                                    evar.get_sources())
        else:
            source_ds = writer.add_event_ds(evar.name,
                                                 evar.get_sources())
        if args.increment <= 0:
            if dialect == nsdf.dialect.ONED:
                writer.add_event_1d(source_ds, evar, fixed=True)
            elif dialect == nsdf.dialect.VLEN:
                writer.add_event_vlen(source_ds, evar, fixed=True)
            if dialect == nsdf.dialect.NANPADDED:
                writer.add_event_nan(source_ds, evar, fixed=True)
        else:
            write_incremental(writer, source_ds, evar,
                              args.increment, args.maxcol,
                              dialect)
    print 'Saved data in', filepath
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Benchmark nsdf writer.')
    parser.add_argument('-d', '--dialect',
                        help='dialect to use: oned, vlen or nan' )
    parser.add_argument('-i', '--increment', type=int, default=0,
                        help='benchmark incremental writing with'
                        ' specified step. 0 means fixed.')
    parser.add_argument('-s', '--sampling', help='sampling type:'
                        ' uniform/u, nonuniform/n, event/e' )
    parser.add_argument('-m', '--mincol', type=int, default=1024,
                        help='minimum number of columns')
    parser.add_argument('-n', '--maxcol', type=int, default=4096,
                        help='maximum number of columns')
    parser.add_argument('-x', '--sources', type=int, default=1024,
                        help='number of sources')
    parser.add_argument('-v', '--variables', type=int, default=1,
                        help='number of variables recorded')
    parser.add_argument('-c', '--compress', 
                        help='enable gzip compression with level=6',
                        action='store_true')
    parser.add_argument('-o', '--out', 
                        help='output data file')
    args = parser.parse_args()
    print args
    data = create_datasets(args)
    write_data(args, data)
        
                                            
        

# 
# benchmark_writer.py ends here
