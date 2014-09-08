# plot_profile_data.py --- 
# 
# Filename: plot_profile_data.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Sat Sep  6 11:19:21 2014 (+0530)
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
import sys
from collections import namedtuple, defaultdict
import csv
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

mpl.rcParams['text.usetex'] = True
# mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]

FIELDNAMES = ['dialect',
              'compression',
              'increment',
              'mincol',
              'maxcol',
              'sampling',
              'sources',
              'variables',
              'event_data',
              'event_ds',
              'nonuniform_data',
              'nonuniform_ds',
              'uniform_data',
              'uniform_ds',
              'write_data']

KEY_FIELDS = ['dialect',
        'compression',
        'increment',
        # 'mincol',
        # 'maxcol',
        # 'sampling',
        # 'sources',
        # 'variables',
]

DATA_FIELDS = ['event_data',
               'event_ds',
               'nonuniform_data',
               'nonuniform_ds',
               'uniform_data',
               'uniform_ds',
               'write_data']

KeyTuple = namedtuple('BenchmarkCond', KEY_FIELDS)

COLORS = {'vlen': 'SteelBlue',
          'oned': 'DarkRed',
          'nan': 'Orange'}

POS = {'oned': 1,
       'vlen': 2,
       'nan': 3}

def plot_profile_data(filename):
    """Plot the processed profiling information for different dialect.
    The profile data is processed into csv files containing the following
    headers:
    
    dialect: dialect of nsdf

    compression: compression level. 0 is no compression 6 is medium
    compression.

    increment: number of columns written at each step for incremental
    writing. 0 means fixed dataset.

    mincol: minimum number of columns for generated event and
    nonuniform data.

    maxcol: maximum number of columns for generated event and
    nonuniform data. This is also the number of columns for generated
    nonuniform data.
    
    sampling: kind of sampling. all means the benchmark script writes
    all three kinds of data in a single run.
    
    sources: number of data sources for each variable. This will be
    the number of rows in the dataset.
    
    variables: number of variables for each sampling type. Although
    the variables could share the same sources, we create different
    source populations for benchmarking purpose.
    
    All the times below are cumulative, i.e. summed over multiple
    calls of the function as required to write the entire dataset.
    
    event_data: time to write event data
    
    event_ds: time to write event data sources (dimension scale)

    nonuniform_data: time to write nonuniform data

    nonuniform_ds: time to write nonuniform data sources (dimension
    scale)

    uniform_data: time to write uniform data

    uniform_ds: time to write uniform data sources (dimension scale)

    write_data: total time to write data file (close to the sum of the
    above times).

    """
    with open(filename, 'rb') as datafile:
        reader = csv.DictReader(datafile)
        data = defaultdict(dict)
        for row in reader:
            print row
            # return
            kdict = {field: row[field] for field in KEY_FIELDS}
            key = KeyTuple(**kdict)
            for field in DATA_FIELDS:
                print field,  row[field]
                values = data[key].get(field, [])
                values.append(float(row[field]))
                data[key][field] = values

    for field in DATA_FIELDS:
        fig = plt.figure()
        # fig.suptitle(field)
        axes_list = []
        ax = None
        for ii in range(4):
            ax = fig.add_subplot(2, 2, ii+1,sharex=ax, sharey=ax)
            ax.get_xaxis().set_visible(False)
            axes_list.append(ax)
            if ii // 2 == 0:
                title = r'\textbf{compressed}' if ii % 2 else r'\textbf{uncompressed}'
                ax.set_title(title)
            if ii % 2 == 0:
                ylabel = r'\textbf{fixed}' if ii // 2 == 0 else r'\textbf{incremental}'
                ylabel += '\nTime (s)'
                ax.set_ylabel(ylabel)
            else:
                ax.get_yaxis().set_visible(False)
            plt.setp(ax, frame_on=False)
        for iii, key in enumerate(data):            
            color = COLORS[key.dialect]
            pos = POS[key.dialect]
            col = 0 if key.compression == '0' else 1
            row = 0 if key.increment == '0' else 1
            ax = axes_list[row * 2 + col]
            ax.bar([pos], np.mean(data[key][field]), yerr=np.std(data[key][field]),
                      color=color, ecolor='b', alpha=0.7,
                      label=key.dialect)
        pdfout = PdfPages('{}.pdf'.format(field))
        pdfout.savefig(fig)
        pdfout.close()
    plt.show()

if __name__ == '__main__':
    filename = sys.argv[1]
    print 'Reading', filename
    plot_profile_data(filename)


# 
# plot_profile_data.py ends here
