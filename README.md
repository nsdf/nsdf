nsdf
====

NSDF (Neuroscience Simulation Data Format) is a file format built
on top of HDF5 <http://www.hdfgroup.org/>.

Although the design and development started with the aim of storing
data generated from simulations in computational neuroscience, this
format is generic enough that any time series data should fit in. Thus
the actual application can be much broader than simulations in
neuroscience.

Requirements
------------

nsdf module works with h5py 2.3.1. Python 2.7 and numpy.
