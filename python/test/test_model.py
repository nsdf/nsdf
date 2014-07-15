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

from nsdf import model

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
        self.assertEqual(self.root.children[0], comp)
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

if __name__ == '__main__':
    unittest.main()



# 
# test_model.py ends here
