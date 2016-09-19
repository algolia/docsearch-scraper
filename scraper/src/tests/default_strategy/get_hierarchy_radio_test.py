# -*- coding: utf-8 -*-

import lxml.html
from .abstract import get_strategy

class TestGetHierarchyRadio:

    def test_toplevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': None,
            'lvl2': None,
            'lvl3': None,
            'lvl4': None,
            'lvl5': None,
            'lvl6': None
        }

        # When
        strategy = get_strategy()
        actual = strategy.get_hierarchy_radio(hierarchy, 'lvl0')

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] is None
        assert actual['lvl2'] is None
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None
        assert actual['lvl6'] is None

    def test_sublevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': 'Bar',
            'lvl2': 'Baz',
            'lvl3': None,
            'lvl4': None,
            'lvl5': None,
            'lvl6': None
        }

        # When
        strategy = get_strategy()
        actual = strategy.get_hierarchy_radio(hierarchy, 'lvl2')

        # Then
        assert actual['lvl0'] is None
        assert actual['lvl1'] is None
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None
        assert actual['lvl6'] is None

    def test_contentlevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': 'Bar',
            'lvl2': 'Baz',
            'lvl3': None,
            'lvl4': None,
            'lvl5': None,
            'lvl6': None
        }

        # When
        strategy = get_strategy()
        actual = strategy.get_hierarchy_radio(hierarchy, 'content')

        # Then
        assert actual['lvl0'] is None
        assert actual['lvl1'] is None
        assert actual['lvl2'] is None
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None
        assert actual['lvl6'] is None