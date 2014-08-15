# nsdfdata.py --- 
# 
# Filename: nsdfdata.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Tue Jul 29 12:55:01 2014 (+0530)
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

"""Classes for NSDF data."""

import numpy as np

class NSDFData(object):
    """Base class for NSDF Data.

    Attributes:

        name (str): name of the dataset.

        unit (str): unit of the recorded quantity.

        field (str): the recorded field/parameter of the source
            object. If unspecified it defaults to `name`.

        dtype (numpy.dtype): type of the recorded data. Default:
            numpy.float64

    """
    def __init__(self, name, unit=None, field=None, dtype=np.float64):
        self.name = name
        self.unit = unit
        self.dtype = dtype
        self.field = name if field is None else field
        self._src_data_dict = {}

    def put_data(self, source, data):
        """Set the data array for source. 
        
        Args:
            source (str):  uid of the data source.

            data (a scalar or sequence of elements of dtype): the data
                for this source.

        Returns:
            None

        """
        self._src_data_dict[source] = np.asarray(data, dtype=self.dtype)

    def get_source_data_dict(self):
        """Return a dictionary storing the mapping from source->data."""
        return self._src_data_dict

    def update_source_data_dict(self, src_data):
        """Insert a bunch of source, data pairs.

        Args:
            src_data (dict-like): an object that is a dict or a
            sequence of key-value pairs.
            
        Returns:
            None

        Examples:
            >>> data_obj = nsdf.UniformData('current', unit='pA')
            >>> ika, ikdr = [0.1, 0.3, 0.5], [0.3, 0.14]
            >>> data_obj.update_source_data_dict([('KA', ika), ('KDR', ikdr)])

        """
        self._src_data_dict.update(src_data)

    def get_sources(self):
        """Return the source ids as a list"""
        return self._src_data_dict.keys()

    def get_all_data(self):
        """Return the data for all the sources as a list."""
        return self._src_data_dict.values()

    def get_data(self, source):
        """Return the data for specified source"""
        return self._src_data_dict[source]

    
class TimeSeriesData(NSDFData):
    def __init__(self, name, unit=None, field=None, tunit=None, dtype=np.float64):
        super(TimeSeriesData, self).__init__(name, unit, field, dtype)
        self.tunit = tunit
        
        
class UniformData(TimeSeriesData):
    """Stores uniformly sampled data.

    Attributes:        
        dt (float): the sampling interval of the data.
    
        tunit (float): unit of time.

    """
    def __init__(self, *args, **kwargs):
        dt = kwargs.pop('dt', 1.0)
        tunit = kwargs.pop('tunit', 's')
        super(UniformData, self).__init__(*args, **kwargs)
        self.dt = dt
        self.tunit = tunit
        
    def set_dt(self, value, unit):
        """Set the timestep used for data recording."""
        self.dt = value
        self.tunit = unit

        
class NonuniformData(TimeSeriesData):
    """Stores nonuniformly sampled data."""
    def __init__(self, *args, **kwargs):
        super(NonuniformData, self).__init__(*args, **kwargs)

    def put_data(self, source, data):
        """Set the data array for source. 
        
        Args:
            source (str):  uid of the data source.

            data (a 2-tuple): the data and sampling times for this
                source.

        Returns:
            None

        """
        assert len(data) == 2, 'need a 2-tuple (data values, sampling times)'
        assert len(data[0]) == len(data[1]),    \
            'number of data values and sampling times must be the same.'
        super(NonuniformData, self).put_data(source, data)

        
class NonuniformRegularData(TimeSeriesData):
    """Stores nonuniformly sampled data where all sources are sampled at
    the same time points."""
    def __init__(self, *args, **kwargs):
        super(NonuniformRegularData, self).__init__(*args, **kwargs)
        self._times = None

    def set_times(self, times, tunit=None):
        """Set the sampling times of all the data points."""
        self._times = times
        if tunit is not None:
            self.tunit = tunit

    def put_data(self, source, data):
        """Set the data array for source. 
        
        Args:
            source (str):  uid of the data source.

            data (a scalar or sequence of elements of dtype): the data
                for this source.

        Returns:
            None

        Raises: 
            ValueError if length of data does not match that of
            sampling times.

        """
        if self._times is None:
            raise ValueError('`sampling_times` must be set before setting data')
        assert len(self._times) == len(data), \
            'length of data must match that of sampling times'
        super(NonuniformRegularData, self).put_data(source, data)

    def get_times(self):
        """Returns the sampling times for the entire dataset."""
        return self._times

    
class EventData(NSDFData):
    """Stores event times recorded from data sources."""
    def __init__(self, *args, **kwargs):
        super(EventData, self).__init__(*args, **kwargs)

        
class StaticData(NSDFData):
    """Stores static data recorded from data sources."""
    def __init__(self, *args, **kwargs):
        super(StaticData, self).__init__(*args, **kwargs)
        

# 
# nsdfdata.py ends here
