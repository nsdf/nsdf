# test_model.py --- 
# 
# Filename: test_model.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Tue Jul 15 16:30:54 2014 (+0530)
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

import unittest
import sys
sys.path.append('..')

from nsdf import model

uid__ = 0
def getuid():
    """Increment the global uid tracker and return the value.

    Returns:
        str representation of the uid integer.
    """
    global uid__
    uid__ += 1
    return str(uid__)


def create_ob_model_tree():
        """This creates a model tree of the structure:

        /model
        |
        |__Granule
        |       |
        |       |__granule_0
        |       |       |__gc_0
        |       |       |__...
        |       |       |__gc_19
         ... ... ...
        |       |
        |       |__granule_9
        |               |__gc_0
        |               |__...
        |               |__gc_19 
        |__Mitral
        |       |
        |       |__mitral_0
        |       |       |__mc_0
        |       |       |__...
        |       |       |__mc_14
         ... ... ...
        |       |
        |       |__mitral_9
        |               |__mc_0
        |               |__...
        |               |__mc_19
       

        """
        uid = 0
        model_tree = model.ModelComponent('model', uid=getuid())
        granule = model.ModelComponent('Granule', uid=getuid(),
                                            parent=model_tree)
        mitral = model.ModelComponent('Mitral', uid=getuid(),
                                           parent=model_tree)
        granule_cells = [model.ModelComponent('granule_{}'.format(ii),
                                                 uid=getuid(),
                                                 parent=granule)
                                                 for ii in range(10)]
        mitral_cells = [model.ModelComponent('mitral_{}'.format(ii),
                                                   uid=getuid(),
                                                   parent=mitral)
                                                 for ii in range(10)]
        for cell in granule_cells:
            cell.add_children([model.ModelComponent('gc_{}'.format(ii),
                                                uid=getuid())
                               for ii in range(20)])
        for cell in mitral_cells:
            cell.add_children([model.ModelComponent('mc_{}'.format(ii),
                                                    uid=getuid())
                               for ii in range(15)])
        return {'model_tree': model_tree,
                'granule_population': granule,
                'mitral_population': mitral,
                'granule_cells': granule_cells,
                'mitral_cells': mitral_cells}

class TestModel(unittest.TestCase):
    """Test model and modeltree."""
    def setUp(self):
        self.root = model.ModelComponent('root', '1')
        
    def test_add_child(self):
        name = 'test'
        uid = '123'
        comp = model.ModelComponent(name, uid)
        self.assertEqual(comp.name, name)
        self.assertEqual(comp.uid, uid)
        self.root.add_child(comp)
        self.assertEqual(len(self.root.children), 1)
        self.assertEqual(self.root.children[name], comp)
        self.assertEqual(comp.parent, self.root)

    def test_add_children(self):
        names = ['test_{}'.format(str(ii)) for ii in range(10)]
        comps = [model.ModelComponent(name) for name in names]
        self.root.add_children(comps)
        self.assertEqual(len(self.root.children), len(comps))
        for comp in comps:
            self.assertEqual(comp.parent, self.root)

    def test_add_child_exception(self):
        self.assertRaises(TypeError, self.root.add_child, 'hello')
        
    def test_path(self):
        self.mdict = create_ob_model_tree()
        for cell in self.mdict['granule_cells']:
            self.assertTrue(cell.path.startswith('/model/Granule/granule_'))
            for name, component in cell.children.items():                
                self.assertEqual(component.path, 
                                 '{}/{}'.format(cell.path, name))

if __name__ == '__main__':
    unittest.main()



# 
# test_model.py ends here
