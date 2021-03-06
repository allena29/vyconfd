#!/usr/bin/env python
#
#    test_session.py: integration tests for the session class
#    Copyright (C) 2014 VyOS Development Group <maintainers@vyos.net>
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#    USA

import os
import unittest

import vyconf.tree.configtree as vct
import vyconf.tree.referencetree as vrt
import vyconf.types as vtypes
import vyconf.types.dummy as dummytypes
import vyconf.session as vsession

DATA_DIR = os.environ.get(
    'VYCONF_DATA_DIR',
    os.path.join(os.getcwd(), 'data'))

TEST_DATA_DIR = os.environ.get(
    'VYCONF_TEST_DATA_DIR',
    os.path.join(os.path.join(os.getcwd(), 'vyconf/tests/integration/data')))

xml_0 = "session_test_0.xml"
xml_1 = "session_test_1.xml"
xml_path_0 = os.path.join(TEST_DATA_DIR, xml_0)
xml_path_1 = os.path.join(TEST_DATA_DIR, xml_1)
xmls = [xml_path_0, xml_path_1]
schema_file = "schemas/interface_definition.rng"

schema_path = os.path.join(DATA_DIR, schema_file)


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.user = "vyconfadmin"
        self.types_dict = vtypes.get_types(dummytypes)
        self.rt = vrt.load_reference_tree(
            self.types_dict,
            xmls,
            schema_path)

        self.config_tree = vct.ConfigNode("root")
        self.validator = vrt.PathValidator(tree=self.rt, types=self.types_dict)

    def _make_session(self):
        session = vsession.Session(
            self.config_tree,
            self.validator,
            self.user)
        session.configure()
        return session

    def test_set(self):
        session = self._make_session()
        session.set(['foo', 'bar'])
        self.assertTrue(session.exists(['foo', 'bar']))

    def test_set_with_value(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        self.assertTrue(session.exists(['foo', 'quux', 'spam', 'fgsfds']))

    def test_set_with_value_multi(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        session.set(['foo', 'quux', 'spam', 'vbnm'])
        self.assertTrue(session.exists(['foo', 'quux', 'spam', 'fgsfds']))
        self.assertTrue(session.exists(['foo', 'quux', 'spam', 'vbnm']))

    def test_set_with_value_multi_duplicate(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        self.assertRaises(
            vsession.SessionError,
            session.set,
            ['foo', 'quux', 'spam', 'fgsfds'])

    def test_set_with_value_non_multi(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'eggs', 'fgsfds'])
        session.set(['foo', 'quux', 'eggs', 'fghj'])
        self.assertTrue(session.exists(['foo', 'quux', 'eggs', 'fghj']))
        self.assertFalse(session.exists(['foo', 'quux', 'eggs', 'fgsfds']))

    def test_set_tag_node(self):
        session = self._make_session()
        session.set(
            ['foo', 'bar', 'baz', 'asdf', 'eggs', 'fghj'])
        self.assertTrue(
            session.exists(['foo', 'bar', 'baz', 'asdf', 'eggs', 'fghj']))

    def test_tag_node_exists(self):
        session = self._make_session()
        session.set(
            ['foo', 'bar', 'baz', 'asdf', 'eggs', 'fghj'])
        self.assertTrue(
            session.exists(['foo', 'bar', 'baz', 'asdf']))


    def test_get_values(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        self.assertTrue(
            session.get_values(['foo', 'quux', 'spam']) ==
            ['fgsfds'])

    def test_delete(self):
        session = self._make_session()
        session.set(['foo', 'bar'])
        session.delete(['foo', 'bar'])
        self.assertTrue(session.exists(['foo']))
        self.assertFalse(session.exists(['foo', 'bar']))

    def test_delete_with_value(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        session.delete(['foo', 'quux', 'spam', 'fgsfds'])
        self.assertTrue(session.exists(['foo', 'quux']))
        self.assertFalse(session.exists(['foo', 'quux', 'spam', 'fgsfds']))

    def test_delete_with_multiple_values(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'tyuiop'])
        session.set(['foo', 'quux', 'spam', 'zxcvb'])
        session.delete(['foo', 'quux', 'spam', 'zxcvb'])
        self.assertTrue(session.exists(['foo', 'quux', 'spam', 'tyuiop']))
        self.assertFalse(session.exists(['foo', 'quux', 'spam', 'zxcvb']))

    def test_delete_subtree(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'fgsfds'])
        session.delete(['foo', 'quux'])
        self.assertTrue(session.exists(['foo']))
        self.assertFalse(session.exists(['foo', 'quux', 'spam', 'fgsfds']))

    def test_set_get_level(self):
        session = self._make_session()
        session.set_level(['foo', 'quux'])
        self.assertEqual(session.get_level(), ['foo', 'quux'])

    def test_reset_level(self):
        session = self._make_session()
        session.set_level(['foo', 'quux'])
        session.set_level([])
        self.assertEqual(session.get_level(), [])

    def test_set_with_level(self):
        session = self._make_session()
        session.set_level(['foo', 'quux'])
        session.set(['spam', 'asdf'])
        session.set_level([])
        self.assertTrue(session.exists(['foo', 'quux', 'spam', 'asdf']))

    def test_delete_with_level(self):
        session = self._make_session()
        session.set_level(['foo', 'quux'])
        session.set(['spam', 'rtyu'])
        session.delete(['spam', 'rtyu'])
        session.set_level([])
        self.assertFalse(session.exists(['foo', 'quux', 'spam', 'rtyu']))

    def test_set_get_comment(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'rtyu'])
        session.set_comment(['foo', 'quux', 'spam'],
                            "test")
        self.assertEqual(session.get_comment(
                         ['foo', 'quux', 'spam']),
                         "test")

    def test_get_status_added(self):
        session = self._make_session()
        session.set(['foo', 'quux', 'spam', 'asdf'])
        status = session.get_node_status(['foo', 'quux', 'spam'])
        self.assertEqual(status, vsession.ADDED)

