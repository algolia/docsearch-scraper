# -*- coding: utf-8 -*-

from .abstract import get_strategy
from ...strategies.hierarchy import Hierarchy


class TestGetHierarchyComplete:

    def test_simple_toplevel(self):
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
        actual = Hierarchy.get_hierarchy_complete(hierarchy, strategy.levels)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] is None
        assert actual['lvl2'] is None
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None
        assert actual['lvl6'] is None

    def test_many_levels(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': 'Bar',
            'lvl2': 'Baz',
            'lvl3': None,
            'lvl4': None,
            'lvl5': None,
            'lvl6': None,
        }

        # When
        strategy = get_strategy()
        actual = Hierarchy.get_hierarchy_complete(hierarchy, strategy.levels)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Foo > Bar'
        assert actual['lvl2'] == 'Foo > Bar > Baz'
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None
        assert actual['lvl6'] is None
