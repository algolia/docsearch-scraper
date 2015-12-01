"""DocumentationSpider tests"""
from documentation_spider import DocumentationSpider
from lxml.cssselect import CSSSelector
import lxml

SELECTORS = {
    "lvl0": "h1",
    "lvl1": "h2",
    "lvl2": "h3",
    "lvl3": "h4",
    "lvl4": "h5",
    "lvl5": "h6",
    "text": "p"
}
SPIDER = DocumentationSpider(
    "test",
    "allowed_domains",
    "start_urls",
    "stop_urls",
    SELECTORS,
    "selector_exclude",
    "strip_chars"
    "algolia_helper",
    "strategy",
    1
)

class TestGetHierarchyRadio:

    def test_simple_toplevel(self):
        # Given
        content = 'Foo'
        level = 'lvl0'

        # When
        actual = SPIDER.get_hierarchy_radio(content, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_simple_sublevel(self):
        # Given
        content = 'Baz'
        level = 'lvl2'

        # When
        actual = SPIDER.get_hierarchy_radio(content, level)

        # Then
        assert actual['lvl0'] == None
        assert actual['lvl1'] == None
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

class TestGetHierarchy:
    """Test the get_hierarchy method"""

    def test_simple_toplevel(self):
        # Given
        dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl0'
        element = CSSSelector(SELECTORS[level])(dom)[0]

        # When
        actual = SPIDER.get_hierarchy(dom, element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_simple_sublevel(self):
        # Given
        dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'lvl1'
        element = CSSSelector(SELECTORS[level])(dom)[0]

        # When
        actual = SPIDER.get_hierarchy(dom, element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_no_parent(self):
        # Given
        dom = lxml.html.fromstring("""
        <html><body>
            <p>Text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)
        level = 'text'
        element = CSSSelector(SELECTORS[level])(dom)[0]

        # When
        actual = SPIDER.get_hierarchy(dom, element, level)

        # Then
        assert actual['lvl0'] == None
        assert actual['lvl1'] == None
        assert actual['lvl2'] == None
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_different_wrappers(self):
        # Given
        dom = lxml.html.fromstring("""
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
        element = CSSSelector(SELECTORS[level])(dom)[0]

        # When
        actual = SPIDER.get_hierarchy(dom, element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None

    def test_selector_contains_elements(self):
        # Given
        dom = lxml.html.fromstring("""
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
        element = CSSSelector(SELECTORS[level])(dom)[0]

        # When
        actual = SPIDER.get_hierarchy(dom, element, level)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Bar'
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
        actual = SPIDER.get_hierarchy_complete(hierarchy)

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
        actual = SPIDER.get_hierarchy_complete(hierarchy)

        # Then
        assert actual['lvl0'] == 'Foo'
        assert actual['lvl1'] == 'Foo > Bar'
        assert actual['lvl2'] == 'Foo > Bar > Baz'
        assert actual['lvl3'] == None
        assert actual['lvl4'] == None
        assert actual['lvl5'] == None
