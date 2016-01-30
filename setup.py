import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="nsdf",
      version="0.1",
      author="Subhasis Ray and Chaitanya Chintaluri",
      author_email="ray dot subhasis at gmail dot com",
      description=("NSDF (Neuroscience Simulation Data Format)"),
      license="GPL 3",
      keywords="neuroscience simulation format data",
      url="https://github.com/nsdf/nsdf",
      download_url="https://github.com/nsdf/nsdf/tarball/0.1",
      packages=['nsdf', 'nsdf.test'],
      long_description=read('README.md'),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
      ],
      install_requires=[
          "cython",
          "h5py"
      ])
