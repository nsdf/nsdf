nsdf
====

NSDF (Neuroscience Simulation Data Format) is a file format built
on top of [HDF5](http://www.hdfgroup.org/).

Although the design and development started with the aim of storing
data generated from simulations in computational neuroscience, this
format is generic enough that any time series data should fit in. Thus
the actual application can be much broader than simulations in
neuroscience.

 * NSDF is under development and we welcome feedback and suggestions from
the community.

 * If you use nsdf for your research, please consider citing the article with NSDF specification:
 
 Ray, Subhasis, Chaitanya Chintaluri, Upinder S. Bhalla, and Daniel K. Wójcik. 2015. "NSDF: Neuroscience Simulation Data Format." Neuroinformatics, November, 1–21. doi:10.1007/s12021-015-9282-5.


Requirements
------------

nsdf module works with h5py 2.3.1. Python 2.7 and numpy. The latest
development version should also work with Python 3, but not fully
tested yet.

To build the documentation you also need sphinx,
sphinxcontrib-napoleon packages.


Installation
------------
To install from PyPI use: 

1. If you have admin rights on a linux and want to install it for all users:

	`sudo pip install nsdf`

2. If you don't have admin rights or want to install in your home directory

	`pip install nsdf --user`



To install the nsdf package from the source (available at
"https://github.com/nsdf/nsdf"):

Open a terminal, cd to the top level directory (the one containing
this file) and enter:

`python setup.py install`


To build the documentation, cd to doc directory and enter:

`make html`

This will create "\_build" directory and the index of the docs will be
in "\_build/html/index.html". Or you can read the latest documentation
built from git:master branch on nsdf.readthedocs.org.

Other Tools
-----------

[dataviz](https://github.com/subhacom/dataviz)
A GUI utility for viewing HDF5 datasets.

[Moogli](https://github.com/BhallaLab/moogli/) 
A Simulator independent visualization tool for neuronal simulations.

Credits
-------

Subhasis Ray, Chaitanya Chintaluri, Upinder Bhalla and Daniel Wójcik
have been designing the specification in collaboration.

Chaitanya provided examples and use cases.

Subhasis is developing this Python module providing a high level API
for reading and writing NSDF files.

We thank Aviral Goel, Johannes Rieke and Matteo Cantarelli for their
critical input.

Zbigniew Jędrzejewski-Szmek contributed to structuring for packaging.
