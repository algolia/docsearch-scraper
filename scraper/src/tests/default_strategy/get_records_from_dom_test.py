# -*- coding: utf-8 -*-

from .abstract import get_strategy
import lxml.html

class TestGetRecordsFromDom:
    def test_simple(self):
        # Given
        strategy = get_strategy()
        strategy.dom = lxml.html.fromstring("""
        <html><body>
          <h1>Foo</h1>
          <h2>Bar</h2>
          <h3>Baz</h3>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 3
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

        assert actual[1]['hierarchy']['lvl0'] == 'Foo'
        assert actual[1]['hierarchy']['lvl1'] == 'Bar'
        assert actual[1]['hierarchy']['lvl2'] is None

        assert actual[2]['hierarchy']['lvl0'] == 'Foo'
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] == 'Baz'

    def test_text(self):
        # Given
        strategy = get_strategy()
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] is None
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

    def test_text_with_utf8(self):
        # Given
        strategy = get_strategy()
        strategy.dom = lxml.html.fromstring(u"""
        <html><body>
            <p>UTF8 ‽✗✓ Madness</p>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert actual[0]['type'] == 'content'
        assert actual[0]['content'] == u"UTF8 ‽✗✓ Madness"

    def test_different_wrappers(self):
        # Given
        strategy = get_strategy()
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <header>
              <h1>Foo</h1>
              <p>text</p>
            </header>
            <div>
              <div>
                <div>
                  <h2>Bar</h2>
                  <p>text</p>
                </div>
              </div>
              <div>
                <p>text</p>
                <div>
                  <h3>Baz</h3>
                </div>
              </div>
            </div>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 6
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

        assert actual[2]['hierarchy']['lvl0'] == 'Foo'
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] is None

        assert actual[5]['hierarchy']['lvl0'] == 'Foo'
        assert actual[5]['hierarchy']['lvl1'] == 'Bar'
        assert actual[5]['hierarchy']['lvl2'] == 'Baz'

    def test_selector_contains_elements(self):
        # Given
        strategy = get_strategy()
        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <h1><a href="#">Foo</a><span></span></h1>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

    def test_text_with_only_three_levels(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                'lvl0': 'h1',
                'lvl1': 'h2',
                'lvl2': 'h3',
                'text': 'p'
            }
        })

        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] is None
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

    def test_backward_compatibility_selectors(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                "lvl0": "h1",
                "lvl1": "h2",
                "lvl2": "h3",
                "text": "p"
            },
            'strip_chars': ',.'
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
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo'
        assert actual[3]['hierarchy']['lvl1'] == 'Bar'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz'
        assert actual[3]['content'] == 'text'

    def test_xpath_text_feature(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                "lvl0": "h1",
                "lvl1": "h2",
                "lvl2": "h3",
                "text": {
                    "selector": "//*[@class=\"content\"]/text()[normalize-space()]",
                    "type": "xpath"
                }
            },
            'strip_chars': ',.'
        })

        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <div class="content">
                <h1>Foo</h1>
                <h2>Bar</h2>
                <h3>Baz</h3>
                text
            </div>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo'
        assert actual[3]['hierarchy']['lvl1'] == 'Bar'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz'
        assert actual[3]['content'] == 'text'

    def test_multiple_selectors_set(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                'api': {
                    "lvl0": "h1",
                    "lvl1": "h2",
                    "lvl2": "h3",
                    "content": "p"
                },
                'guide': {
                    "lvl0": "h1",
                },
            },
            'start_urls': [
                {
                    'url': 'http://test.com/docs/guide',
                    'selectors_key': 'guide'
                },
                {
                    'url': 'http://test.com/docs/api',
                    'selectors_key': 'api'
                }
            ]
        })

        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <h1>.Foo;</h1>
            <h2>!Bar.</h2>
            <h3>,Baz!</h3>
            <p>,text,</p>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom('http://test.com/docs/api/methods')

        # Then
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo'
        assert actual[3]['hierarchy']['lvl1'] == '!Bar'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz!'
        assert actual[3]['content'] == 'text'

    def test_multiple_selectors_set_2(self):
        # Given
        strategy = get_strategy({
            'selectors': {
                'api': {
                    "lvl0": "h1",
                    "lvl1": "h2",
                    "lvl2": "h3",
                    "content": "p"
                },
                'guides': {
                    "lvl0": "h1",
                },
            },
            'start_urls': [
                {
                    'url': 'http://test.com/docs/guides',
                    'selectors_key': 'guides'
                },
                {
                    'url': 'http://test.com/docs/api',
                    'selectors_key': 'api'
                }
            ]
        })

        strategy.dom = lxml.html.fromstring("""
        <html><body>
            <h1>.Foo;</h1>
            <h2>!Bar.</h2>
            <h3>,Baz!</h3>
            <p>,text,</p>
        </body></html>
        """)

        # When
        actual = strategy.get_records_from_dom('http://test.com/docs/guides/tutorial1')

        # Then
        assert len(actual) == 1
        assert actual[0]['type'] == 'lvl0'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
