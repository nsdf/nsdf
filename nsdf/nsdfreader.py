# nsdfreader.py --- 
# 
# Filename: nsdfreader.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Sat Aug  9 14:49:04 2014 (+0530)
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

"""Reader for NSDF format"""

import h5py as h5
import numpy as np

from .model import ModelComponent, common_prefix
from .constants import *
from .util import *
from .nsdfdata import *
from datetime import datetime


class NSDFReader(object):
    """Reader for NSDF files.
    
    This class encapsulates an NSDF file and provides utility
    functions to read the data in an organized manner.

    

    """
    def __init__(self, filename):
        self._fd = h5.File(filename, 'r')
        self.data = self._fd['data']
        self.model = self._fd['model']
        self.mapping = self._fd['map']
        self.dialect = str(self._fd.attrs['dialect'])

    def __del__(self):
        self._fd.close()

    @property
    def uniform_populations(self):
        """Names of the populations for which variables have been recorded
        with uniform sampling.

        """
        return self.data['uniform'].keys()
    
    @property
    def nonuniform_populations(self):
        """Names of the populations for which variables have been recorded
        with nonuniform sampling.

        """
        return self.data['nonuniform'].keys()

    @property
    def event_populations(self):
        """Names of the populations for which event variables have been
        recorded.

        """
        return self.data['event'].keys()

    def get_uniform_vars(self, population):
        """Returns the names of uniform variables recorded for `population`.

        Args:        
            population (str): name of the population.

        Returns:
            list of str: names of the datasets storing uniform variables.

        """
        return self.data['uniform'][population].keys()

    def get_nonuniform_vars(self, population):
        """Returns the names of nonuniform variables recorded for `population`.

        Args:        
            population (str): name of the population.

        Returns:
            list of str: names of the groups storing nonuniform variables.

        """
        return self.data['nonuniform'][population].keys()

    
    def get_event_vars(self, population):
        """Returns the names of event variables recorded for `population`.

        Args:        
            population (str): name of the population.

        Returns:
            list of str: names of the groups storing event variables.

        """
        return self.data['event'][population].keys()

    def get_uniform_dataset(self, population, varname):
        """Returns the data sources and data contents for recorded variable
        `varname` from `population`.

        Args:
            population (str): name of the population.

            varname (str): name of the variable.

        Returns:

            (sources, data): `sources` is an dataset containing the
                source identifiers and data is a 2D dataset whose i-th
                row is the data from the i-th entry in `sources`.

        """
        return (self.mapping['uniform'][population][varname],
                self.data['uniform'][population][varname])

    def _get_or_create_uniform_ts(self, dataset):
        try:
            tstart = dataset.attrs['tstart']
            dt = dataset.attrs['dt']
            tunit = dataset.attrs['tunit']
            ts = np.arange(dataset.shape[1], dtype=np.double) * dt + tstart
        except KeyError:
            ts = dataset.dims[1]['time']
            tunit = ts.attrs['unit']
        return (ts, tunit)
        

    def get_uniform_ts(self, population, varname):
        """Returns an array of sampling times and time-unit for the uniform
        dataset `varname` recorded from `population`.

        Args:
            population (str): name of the population of sources.

            varname (str): name of the recorded variable.

        Returns: 
            (times, unit) : times is an array of doubles containing
                the sampling time for each column of the dataset and
                unit is a string representing the unit of time.

        """
        data = self.data['uniform'][population][varname]
        return self._get_or_create_uniform_ts(data)

    def get_uniform_dt(self, population, varname):
        """Returns sampling interval and time-unit for the uniform dataset
        `varname` recorded from `population`.

        Args:
            population (str): name of the population of sources.

            varname (str): name of the recorded variable.

        Returns: 
            (dt, unit) : `dt` is the sampling interval for this dataset and
                unit is a string representing the unit of time.

        """
        data = self.data['uniform'][population][varname]
        try:
            dt = data.attrs['dt']
            tunit = data.attrs['tunit']
            return (dt, tunit)
        except KeyError:
            ts = data.dims[1]['time']
            tunit = ts.attrs['unit']
        return (ts[1]-ts[0], tunit)

    def get_uniform_row(self, srcid, field):
        """Get the data for `field` variable recorded from source with
        unique id `srcid`.

        Args:
            srcid (str): unique id of the source.

            varname (str): name of the variable.

        Returns:
            (data, unit, times, timeunit)

        """
        for srcmap in self.mapping['uniform']:
            sources = np.asarray(srcmap, dtype=str)
            indices = np.where(sources == srcid)[0]
            if indices:
                index = indices[0]
                for refinfo, dtype in sources.attrs['REFERENCE_LIST']:
                    ref = refinfo[0]
                    dataset = self._fd[ref]
                    if dataset.attrs['field'] == field:
                        data = np.asarray(dataset[index])
                        unit =  dataset.attrs['unit']
                        ts, tunit = self._get_or_create_uniform_ts(dataset)
                        return (data, unit, ts, tunit)

    def get_uniform_data(self, population, variable):
        """Returns a UniformData object contents for recorded `variable`
        from `population`.

        Args:
            population (str): name of the population.

            variable (str): name of the variable.

        Returns:

            dataobject (nsdf.UniformData): data container filled with
                source, data, dt and units.

        """
        data = self.data['uniform'][population][variable]
        mapping = self.mapping['uniform'][population]
        ret = UniformData(data.name.rpartition('/')[-1],
                               unit=data.attrs['unit'],
                               field=data.attrs['field'],
                               dt=data.attrs['dt'],
                               tunit=data.attrs['tunit'])
        for src, row in izip(mapping, data):
            ret.put_data(src, row)
        return ret
        
                                
                
            
        
# 
# nsdfreader.py ends here
