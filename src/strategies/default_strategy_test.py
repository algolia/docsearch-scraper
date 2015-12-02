"""DefaultStrategy tests"""
from config_loader import ConfigLoader
from strategies.default_strategy import DefaultStrategy
import lxml.html
import json
import os

SELECTORS = {
    "lvl0": "h1",
    "lvl1": "h2",
    "lvl2": "h3",
    "lvl3": "h4",
    "lvl4": "h5",
    "lvl5": "h6",
    "text": "p"
}
# Stub ENV variables read by ConfigLoader
os.environ['CONFIG'] = json.dumps({
    'allowed_domains': 'test',
    'api_key': 'test',
    'app_id': 'test',
    'custom_settings': 'test',
    'hash_strategy': 'test',
    'index_name': 'test',
    'index_name': 'test',
    'index_prefix': 'test',
    'selectors': SELECTORS,
    'selectors_exclude': 'test',
    'start_urls': 'test',
    'stop_urls': 'test',
    'strategy': 'test',
    'strip_chars': 'test'
})

STRATEGY = DefaultStrategy(ConfigLoader())

class TestGetHierarchy:
    """Test the get_hierarchy method"""

    def test_simple_toplevel(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl0'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_hierarchy(element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_simple_sublevel(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_hierarchy(element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_no_parent(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>Text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'text'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_hierarchy(element, level)

        # Then
        assert actual['lvl0'] == None
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_different_wrappers(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
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
        level = 'lvl2'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_hierarchy(element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_selector_contains_elements(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <header>
              <h1>Foo</h1>
              <p>text</p>
            </header>
            <div>
              <h2><a href="#">Bar</a><span></span></h2>
              <p>text</p>
            </div>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl2'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_hierarchy(element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

class TestGetHierarchyRadio:

    def test_toplevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': None,
            'lvl2': None,
            'lvl3': None,
            'lvl4': None,
            'lvl5': None
        }

        # When
        actual = STRATEGY.get_hierarchy_radio(hierarchy)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_sublevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': 'Bar',
            'lvl2': 'Baz',
            'lvl3': None,
            'lvl4': None,
            'lvl5': None
        }

        # When
        actual = STRATEGY.get_hierarchy_radio(hierarchy)

        # Then
        assert actual['lvl0'] == None
        assert actual['lvl1'] == None
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

class TestGetHierarchyComplete:

    def test_simple_toplevel(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': None,
            'lvl2': None,
            'lvl3': None,
            'lvl4': None,
            'lvl5': None
        }

        # When
        actual = STRATEGY.get_hierarchy_complete(hierarchy)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_many_levels(self):
        # Given
        hierarchy = {
            'lvl0': 'Foo',
            'lvl1': 'Bar',
            'lvl2': 'Baz',
            'lvl3': None,
            'lvl4': None,
            'lvl5': None
        }

        # When
        actual = STRATEGY.get_hierarchy_complete(hierarchy)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Foo > Bar'
        assert actual['lvl2'] == 'Foo > Bar > Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

class TestGetAnchor:

    def test_name_on_heading(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2 name="bar">Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_anchor(element, level)

        # Then
        assert actual == 'bar'

    def test_id_on_heading(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2 id="bar">Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_anchor(element, level)

        # Then
        assert actual == 'bar'

    def test_anchor_on_parent(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1 id="foo">Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_anchor(element, level)

        # Then
        assert actual == 'foo'

    def test_anchor_in_subelement(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2><a href="#" name="bar">Bar</a><span></span></h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_anchor(element, level)

        # Then
        assert actual == 'bar'

    def test_no_anchor(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl2'
        element = STRATEGY.cssselect(SELECTORS[level])[0]

        # When
        actual = STRATEGY.get_anchor(element, level)

        # Then
        assert actual == None

class TestGetLevelWeight:

    def test_level_weight(self):
        assert STRATEGY.get_level_weight('lvl0') == 100
        assert STRATEGY.get_level_weight('lvl1') == 90
        assert STRATEGY.get_level_weight('lvl2') == 80
        assert STRATEGY.get_level_weight('lvl3') == 70
        assert STRATEGY.get_level_weight('lvl4') == 60
        assert STRATEGY.get_level_weight('lvl5') == 50
        assert STRATEGY.get_level_weight('text') == 0
