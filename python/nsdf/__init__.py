"""
.. _nsdf-label:
NSDF
====

NSDF (Neuroscience Simulation Data Format) is a file format built
on top of HDF5 <http://www.hdfgroup.org/>.

Although the design and development started with the aim of storing
data generated from simulations in computational neuroscience, this
format is generic enough that any time series data should fit in. Thus
the actual application can be much broader than simulations in
neuroscience.

There are three top level groups in an NSDF file: `model`, `data` and
`map` for storing information about the model (computational model of
a neuron, the human brain, model of the world, etc.), data collected
from model components and the mapping between the data and its source
(model component) respectively.

.. _data-label
Data
----

NSDF stores the data collected from a model under the `/data` group.
Data is organized into four subgroups:

uniform: Time series data that has been sampled with a uniform
    sampling interval. This is the case for simulations that use fixed
    time step for integration. In this case the sampling interval `dt`
    and the start time is enough to determine the sampling time of any
    data point unambiguously.

nonuniform: Time series data that has been sampled with irregular
    sampling interval. In this case sampling time for each data point
    must be explicitly stored. This is the case for simulations using
    variable time step inetgration methods, like `cvode`.

    There can be several scenarios under nonuniform sampling. 

    1. simultaneous sampling: Although the sampling intervals are
           different, all data sources are sampled simultaneously.
           Thus the length of data from each source is same and data
           points with the same index have the same sampling time. In
           this case, data from an entire population of data sources
           can be put together in a homogeneous 2D dataset and the
           share the sampling times.

           This is the case when the CVODE solver is global for a
           simulation.

           This is represented by the dialect nsdf.dialect.NUREGULAR.

    2. independent sampling: In a more general case, the data should
           be sampled more densely when the variable is changing fast
           and sparsely when the rate of change is slow. If the data
           sources are independent of each other, they may be sampled
           at different time points. Thus data recorded for a fixed
           duration will of different length for different sources. 

           In this case data from a population of sources can be
           stored as:

              a) individual 1D datasets under a common group.

                 nsdf.dialect.ONED represents this case

              b) 2D vlen(variable length) dataset which represents a
                 ragged array with each row having a different number
                 of columns.

                 This is represented by nsdf.dialect.VLEN

              c) 2D dataset with NaN padding such that all rows have
                 same number of columns.

                 This is represented by nsdf.dialect.NANPADDED.

event: Data points represent event times. Spike time data is the most
    common example in neuroscience. Similar to nonunform data, event
    times data from different sources are of different length. Thus
    they, too, can be stored in three different ways.

              a) individual 1D datasets under a common group.

                 nsdf.dialect.ONED represents this case

              b) 2D vlen(variable length) dataset which represents a
                 ragged array with each row having a different number
                 of columns.

                 This is represented by nsdf.dialect.VLEN.

              c) 2D dataset with NaN padding such that all rows have
                 same number of columns.

                 This is represented by nsdf.dialect.NANPADDED.

static: In addition to time series or temporal data, components in a
    model can have static data associated with them. These are stored
    under the `static` group.

.. _model-label:
Model
-----

The `model` group stores information about the model of the system
from which data has been collected. This is relatively free form since
different fields use different ways of describing the model. Within
computational neuroscience there are multiple standards for model
description. NSDF specification provides some containers for storing
model description and one hierarchical structure that can be
immediately useful for data analysis and visualization tools in
neuroscience.

filecontents: This group can have a hierarchical structure underneath
    mapping the directory tree used for the model. Complex models are
    often organized in a directory tree and this maps nicely to the
    hieararchical structure in HDF5, where Groups can represent
    directories and Datasets can represent files. The contents of the
    files can be stored as strings or binary objects in the Datasets.

filerefs: This group can store datasets containing the paths of
    external model files. The disadvantage being that the model has to
    be distributed separately from the data.

links: This group can store links to external model definitions in
    other HDF5 files.

modeltree: This group stores a tree structure representing
    hierarchical models. NSDF provides mechanisms for efficient
    linking between the model components represented by the nodes of
    this tree with the data. 

    Each node in this tree is a Group with a `uid` attribute storing
    the unique identifier of the model component. There can be other
    attributes added by the user. One special attribute is `ontology`
    meant for storing the ontological term for this component.

.. _map-label:
Map
---

Mapping between data and its source is stored under the `/map`
group. Like `/data`, it has the subgroups `uniform`, `nonuniform`,
`event` and `static` which store the mapping between the datasets
under corresponding subgroups of `/data` and the model components.

For all datasets except event and nonuniform data stored in 1D
datasets, the uid of a population of sources are stored as a dataset
under the corresponding group and linked to the datasets recorded from
these as a HDF5 DimensionScale (DS). Multiple variables recorded from
the same source population share this dimension scale. The rows in the
population DS have one to one correspondence with the rows in the
datasets.

For 1D datasets, a 2 column dataset is created for each population for
each recorded variable. The first column is `source` and stores the
uid of the source component and the second column is `data` which
stores the reference to the 1D dataset collected from this source.


Note on namespace
-----------------

The nsdf package is organized into :ref:`constants`, :ref:`nsdfdata`,
:ref:`model`, :ref:`nsdfwriter` and :ref:`util` submodules. However all their
contents are directly accessible under the `nsdf` namespace. Thus,
instead of `nsdf.nsdfwriter.NSDFWriter` you should use
`nsdf.NSDFWriter`.

"""
__author__ = 'Subhasis Ray'
__version__ = '0.1'

from .constants import *
from .util import *
from .model import *
from .nsdfdata import *
from .nsdfwriter import *

# from .NSDFWriter import NSDFWriter as writer
