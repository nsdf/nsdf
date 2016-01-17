"""Example NSDF file storing data from a Hodgkin-Huxley-type
compartment.

"""

__author__ = 'Subhasis Ray'
__date__ = 'Fri Aug  1 21:43:07 IST 2014'

import sys
sys.path.append('..')
import numpy as np
from datetime import datetime, timedelta
from uuid import uuid1

import nsdf

vm_array = np.random.rand(100) - 65.0
ina = np.random.rand(100)
ik = np.random.rand(100)

def hh_vm():
    model = nsdf.ModelComponent('compartment')
    data_container = nsdf.UniformData('Vm', unit='mV', dt=0.1, tunit='ms')
    data_container.put_data(model.uid, vm_array)                            
    writer = nsdf.NSDFWriter('hh_vm.h5', mode='w')
    writer.set_properties({'title': 'Example Vm recording',
                           'creator': 'user',
                           'software': ['python2.7', 'python-nsdf-0.1'],
                           'method': ['np.random.rand'],
                           'description': 'Randomly generated Vm for a single' \
                                          'compartment',
                           'rights': 'CC-BY-SA',
                           'tstart': datetime.now(),
                           'tend': (datetime.now() + timedelta(seconds=3)),
                           'contributor': ['Chaitanya Chintaluri',
                                           'Daniel Wocjcik',
                                           'Upinder Bhalla']})
                           
    writer.add_modeltree(model)
    source_ds = writer.add_uniform_ds('compartment_population', [model.uid])
    writer.add_uniform_data(source_ds, data_container)

    
def read_hh_vm():
    reader = nsdf.NSDFReader('hh_vm.h5')
    data = reader.get_uniform_data('compartment_population', 'Vm')


def hh_compartment():
    filename = 'hh_compartment.h5'
    model = nsdf.ModelComponent('compartment', uid=uuid1().hex)
    writer = nsdf.NSDFWriter(filename, mode='w')
    writer.add_modeltree(model)
    source_ds = writer.add_static_ds(model.name, [model.uid])
    # Add membrane resitance
    data_obj = nsdf.StaticData('Rm', unit='Mohm')
    data_obj.put_data(model.uid, 1e3)
    writer.add_static_data(source_ds, data_obj)
    # Add membrane capacitance
    data_obj = nsdf.StaticData('Cm', unit='pF')
    data_obj.put_data(model.uid, 0.9)
    writer.add_static_data(source_ds, data_obj)
    # Add leak reversal potential
    data_obj = nsdf.StaticData('Em', unit='mV')
    data_obj.put_data(model.uid, -65.0)
    writer.add_static_data(source_ds, data_obj)
    # Add membrane potential
    source_ds = writer.add_uniform_ds(model.name, [model.uid])
    data_obj = nsdf.UniformData('Vm', unit='mV', dt=0.1, tunit='ms')
    data_obj.put_data(model.uid, vm_array)
    writer.add_uniform_data(source_ds, data_obj)
    

def hh_compartment_with_channels():
    filename = 'hh_compartment_with_channels.h5'
    compartment = nsdf.ModelComponent('compartment', uid=uuid1().hex)
    na_channel = nsdf.ModelComponent('NaChannel', uid=uuid1().hex,
                                     parent=compartment)
    k_channel =  nsdf.ModelComponent('KChannel', uid=uuid1().hex,
                                     parent=compartment)
    writer = nsdf.NSDFWriter(filename, mode='w')
    writer.add_modeltree(compartment)
    source_ds = writer.add_static_ds(compartment.name, [compartment.uid])
    # Add membrane resitance
    data_obj = nsdf.StaticData('Rm', unit='Mohm')
    data_obj.put_data(compartment.uid, 1e3)
    writer.add_static_data(source_ds, data_obj)
    # Add membrane capacitance
    data_obj = nsdf.StaticData('Cm', unit='pF')
    data_obj.put_data(compartment.uid, 0.9)
    writer.add_static_data(source_ds, data_obj)
    # Add leak reversal potential
    data_obj = nsdf.StaticData('Em', unit='mV')
    data_obj.put_data(compartment.uid, -65.0)
    writer.add_static_data(source_ds, data_obj)
    # Add membrane potential
    source_ds = writer.add_uniform_ds(compartment.name, [compartment.uid])
    data_obj = nsdf.UniformData('Vm', unit='mV')
    data_obj.put_data(compartment.uid,
                      np.random.uniform(low=-67.0, high=-63.0, size=100))
    data_obj.set_dt(0.1, unit='ms')
    writer.add_uniform_data(source_ds, data_obj)
    source_ds = writer.add_uniform_ds('channel', [na_channel.uid,
                                                  k_channel.uid])
    data_obj = nsdf.UniformData('Ik', unit='nA', dt=0.1, tunit='ms')
    data_obj.update_source_data_dict([(na_channel.uid, ina),
                                      (k_channel.uid, ik)])
    writer.add_uniform_data(source_ds, data_obj)
    

if __name__ == '__main__':
    hh_vm()
    read_hh_vm()
    hh_compartment()
    hh_compartment_with_channels()
    
    
    
