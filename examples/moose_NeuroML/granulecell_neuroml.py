# granulecell_neuroml.py ---
#
# Filename: granulecell_neuroml.py
# Description:
# Author: Subhasis Ray
# Maintainer:
# Created: Sun Aug 31 16:58:48 2014 (+0530)
# Version:
# Last-Updated:
# By:
# Update #: 0
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA.
#
#
# Code:
"""This example shows the use of ``/model/filecontents`` group for
storing the entire model and simulation directory in NSDF file.
It uses the Granule cell model in NeuroMLv1.8 by Aditya Gilra
(available as part of MOOSE demos in Demos/neuroml/GranuleCell). The
script there uses the neuroml reader developed by Aditya to simulate
the model in MOOSE.
"""
import os
import numpy as np
import sys
from datetime import datetime

sys.path.append('../..')
sys.path.append('/home/subha/src/moose_async13/python')
sys.path.append('/home/subha/src/moose_async13/Demos/neuroml/GranuleCell')
# You need to include the location of Granule98 and moose module in
# your path. These are: `moose/Demos/neuroml/GranuleCell` and
# `moose/python` respectively where moose is the directory where you
# have moose sources (built).

# These are also located in the folder, /nsdf/examples/moose_NeuroML/. 
import nsdf

import moose
import Granule98 as granule

def example():
    directory = os.path.dirname(granule.__file__)
    current = os.getcwd()
    os.chdir(directory)
    start_time = datetime.now()
    granule.loadGran98NeuroML_L123(granule.filename)
    end_time = datetime.now()
    tvec = np.arange(0.0, granule.runtime, granule.plotdt)
    soma_path = '/cells[0]/Gran_0[0]/Soma_0[0]'
    ca = moose.element('{}/Gran_CaPool_98/data/somaCa'.format(soma_path))
    vm = moose.element('{}/data[0]/somaVm[0]'.format(soma_path))
    os.chdir(current)
    writer = nsdf.NSDFWriter('granulecell.h5', mode='w', compression='gzip')
    writer.add_model_filecontents([directory])
    ca_data = nsdf.UniformData('Ca', unit='mM', dt=granule.plotdt, tunit='s')
    ca_data.put_data(soma_path, ca.vector)
    source_ds = writer.add_uniform_ds('GranuleSoma', [soma_path])
    writer.add_uniform_data(source_ds, ca_data)
    vm_data = nsdf.UniformData('Vm', unit='V', dt=granule.plotdt, tunit='s')
    vm_data.put_data(soma_path, vm.vector)
    writer.add_uniform_data(source_ds, vm_data)
    writer.title = 'Sample NSDF file for olfactory bulb granule cell model'
    writer.description = 'This file stores the entire model' \
    ' directory in `/model/filecontent`'
    writer.tstart = start_time
    writer.tend = end_time
    writer.creator = [os.environ['USER']]
    writer.contributor = ['Subhasis Ray', 'Aditya Gilra']
    writer.license = 'CC BY-SA'
    writer.software = ['Python2.7', 'moose', 'nsdf python library']
    writer.method = ['exponential Euler']
    print 'Finished writing example NSDF file for GranuleCell demo'

if __name__ == '__main__':
    example()
#
# granulecell_neuroml.py ends here
