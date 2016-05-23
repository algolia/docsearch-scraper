# -*- coding: utf-8 -*-

import lxml.html
from abstract import get_strategy

class TestAllowToBypassOneOrMoreLevels:
    def test_get_settings_with_one_non_searchable(self):
        # Given
        strategy = get_strategy({
            'selectors': {
             "lvl0": {
                 "selector": "h1",
                 "searchable": False
             },
             "lvl1": "h2",
             "lvl2": "h3",
             "content": "p"
            }
        })

        # When
        settings = strategy.get_index_settings()

        # Then
        expected_settings = [
            'unordered(hierarchy_radio.lvl1)',
            'unordered(hierarchy_radio.lvl2)',
            'unordered(hierarchy.lvl1)',
            'unordered(hierarchy.lvl2)',
            'content'
        ]

        assert settings['attributesToIndex'] == expected_settings

    def test_get_records_from_dom_with_empty_selector(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                "lvl0": "",
                "lvl1": "h2",
                "lvl2": "h3",
                "content": "p"
            }
        })
        strategy.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
         <h2>Bar</h2>
         <h3>Baz</h3>
         <p>text</p>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 3
        assert actual[2]['type'] == 'content'
        assert actual[2]['hierarchy']['lvl0'] is None
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] == 'Baz'
        assert actual[2]['content'] == 'text'

    def test_get_records_from_dom_with_empty_selector_and_default_value(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                "lvl0": {
                    "selector": "",
                    "default_value": "Documentation"
                },
                "lvl1": "h2",
                "lvl2": "h3",
                "content": "p"
            }
        })
        strategy.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
         <h2>Bar</h2>
         <h3>Baz</h3>
         <p>text</p>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 3
        assert actual[2]['type'] == 'content'
        assert actual[2]['hierarchy']['lvl0'] == 'Documentation'
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] == 'Baz'
        assert actual[2]['content'] == 'text'
