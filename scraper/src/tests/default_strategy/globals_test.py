# -*- coding: utf-8 -*-

import lxml.html
from abstract import get_strategy

class TestGetRecordsFromDomWithGlobalLevels:
    def test_global_title_at_the_end(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                'lvl0': {
                    'selector': 'h1',
                    'global': 'true'
                },
                'lvl1': 'h2',
                'lvl2': 'h3',
                'text': 'p'
            }
        })
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'

        assert actual[3]['type'] == 'lvl0'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo'
        assert actual[3]['hierarchy']['lvl1'] is None
        assert actual[3]['hierarchy']['lvl2'] is None

    def test_several_match_for_global_selector(self):
        # Given
        strategy = get_strategy({
            'selectors':{
                'lvl0': {
                    'selector': 'h1',
                    'global': 'true'
                },
                'lvl1': 'h2',
                'lvl2': 'h3',
                'content': 'p'
            }
        })
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
            <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert actual[3]['type'] == 'lvl0'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[3]['hierarchy']['lvl1'] is None
        assert actual[3]['hierarchy']['lvl2'] is None


    def test_several_global_selectors(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                'lvl0': {
                    'selector': 'h1',
                    'global': True
                },
                'lvl1': {
                    'selector': 'h2',
                    'global': 'true'
                },
                'lvl2': 'h3',
                'content': 'p'
            }
        })
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
            <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[0]['hierarchy']['lvl1'] == 'Bar'
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'
