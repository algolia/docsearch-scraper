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
    "content": "p"
}
# Stub ENV variables read by ConfigLoader
os.environ['CONFIG'] = json.dumps({
    'allowed_domains': 'test',
    'api_key': 'test',
    'app_id': 'test',
    'custom_settings': None,
    'hash_strategy': 'test',
    'index_name': 'test',
    'index_prefix': 'test',
    'selectors': SELECTORS,
    'selectors_exclude': 'test',
    'start_urls': 'test',
    'stop_urls': 'test',
    'strategy': 'test',
    'strip_chars': ''
})

STRATEGY = DefaultStrategy(ConfigLoader())
SELECTORS = STRATEGY.parse_selectors(SELECTORS)

class TestGetRecordsFromDom:

    def test_simple(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
          <h1>Foo</h1>
          <h2>Bar</h2>
          <h3>Baz</h3>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom()

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
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] is None
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

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

        # When
        actual = STRATEGY.get_records_from_dom()

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
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1><a href="#">Foo</a><span></span></h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None


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
        assert actual['lvl1'] is None
        assert actual['lvl2'] is None
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None

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
        assert actual['lvl0'] is None
        assert actual['lvl1'] is None
        assert actual['lvl2'] == 'Baz'
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None

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
        assert actual['lvl1'] is None
        assert actual['lvl2'] is None
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None

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
        assert actual['lvl3'] is None
        assert actual['lvl4'] is None
        assert actual['lvl5'] is None

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
        element = STRATEGY.select(SELECTORS[level]['selector'])[0]

        # When
        actual = STRATEGY.get_anchor(element)

        # Then
        assert actual == 'bar'

    def test_id_not_in_a_direct_parent(self):
        STRATEGY.dom = lxml.html.fromstring("""
        <div>
            <a id="bar"></a>
            <div>
                <div>
                    <h2>Bar</h2>
                </div>
            </div>
        </div>
        """)

        level = 'lvl1'
        element = STRATEGY.select(SELECTORS[level]['selector'])[0]

        # When
        actual = STRATEGY.get_anchor(element)

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
        element = STRATEGY.select(SELECTORS[level]['selector'])[0]

        # When
        actual = STRATEGY.get_anchor(element)

        # Then
        assert actual == 'bar'

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
        element = STRATEGY.select(SELECTORS[level]['selector'])[0]

        # When
        actual = STRATEGY.get_anchor(element)

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
        element = STRATEGY.select(SELECTORS[level]['selector'])[0]

        # When
        actual = STRATEGY.get_anchor(element)

        # Then
        assert actual is None

class TestGetLevelWeight:

    def test_level_weight(self):
        assert STRATEGY.get_level_weight('lvl0') == 100
        assert STRATEGY.get_level_weight('lvl1') == 90
        assert STRATEGY.get_level_weight('lvl2') == 80
        assert STRATEGY.get_level_weight('lvl3') == 70
        assert STRATEGY.get_level_weight('lvl4') == 60
        assert STRATEGY.get_level_weight('lvl5') == 50
        assert STRATEGY.get_level_weight('text') == 0

class TestGetRecordsFromDom2:
    def test_text_with_only_three_levels(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': 'h1',
            'lvl1': 'h2',
            'lvl2': 'h3',
            'text': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] is None
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None

class TestGetRecordsFromDomWithGlobalLevels:
    def test_global_title_at_the_end(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'h1',
                'global': 'true'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'text': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

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
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
            <h1>Foo</h1>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'h1',
                'global': 'true'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert actual[3]['type'] == 'lvl0'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[3]['hierarchy']['lvl1'] is None
        assert actual[3]['hierarchy']['lvl2'] is None


    def test_several_global_selectors(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <h1>Foo</h1>
            <h1>Foo</h1>
        </body></html>
        """)

        STRATEGY.set_selectors({
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
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[0]['hierarchy']['lvl1'] == 'Bar'
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'

class TestGetRecordsFromDomWithXpath:
    def test_one_xpath(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1 class="title">Foo</h1>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'descendant-or-self::*[@class and contains(concat(\' \', normalize-space(@class), \' \'), \' title \')]',
                'type': 'xpath'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 4
        assert actual[0]['type'] == 'lvl0'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] is None

    def test_two_xpath_including_one_global(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2 class="subtitle">Bar</h2>
            <h3>Baz</h3>
            <h1 class="title">Foo</h1>
            <h1 class="title">Foo</h1>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'descendant-or-self::*[@class and contains(concat(\' \', normalize-space(@class), \' \'),'
                            ' \' title \')]',
                'type': 'xpath',
                'global': True
            },
            'lvl1': {
                'selector': 'descendant-or-self::*[@class and contains(concat(\' \', normalize-space(@class), \' \'),'
                            ' \' subtitle \')]',
                'type': 'xpath'
            },
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'

        assert actual[1]['type'] == 'lvl1'
        assert actual[1]['hierarchy']['lvl0'] == 'Foo Foo'
        assert actual[1]['hierarchy']['lvl1'] == 'Bar'
        assert actual[1]['hierarchy']['lvl2'] is None
        assert actual[1]['content'] is None

    def test_select_parent_with_xpath(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h3>Baz</h3>
            <div>
                <h1 class="title">Foo</h1>
                <div>
                    <ul>
                        <li class="active">Bar</li>
                        <li>Bar 2</li>
                    </ul>
                </div>
            </div>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': '//li[@class="active"]/../../../*[@class="title"]',
                'type': 'xpath',
                'global': True
            },
            'lvl1': 'li.active',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 4
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'


class TestGetRecordsFromDomWithDefaultValue:
    def test_default_value(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'h1',
                'default_value': 'Documentation'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 3
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Documentation'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'

    def test_default_value_for_text(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': 'h1',
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': {
                'selector': 'p',
                'default_value': 'Documentation'
            }
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 3
        assert actual[0]['type'] == 'lvl0'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'Documentation'

    def test_default_value_with_global(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'h1',
                'global': True,
                'default_value': 'Documentation'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 3
        assert actual[0]['type'] == 'content'
        assert actual[0]['hierarchy']['lvl0'] == 'Documentation'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] == 'text'

    def test_default_value_should_not_override(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <p>text</p>
            <h2>Bar</h2>
            <h3>Baz</h3>
        </body></html>
        """)

        STRATEGY.set_selectors({
            'lvl0': {
                'selector': 'h1',
                'global': True,
                'default_value': 'Documentation'
            },
            'lvl1': 'h2',
            'lvl2': 'h3',
            'content': 'p'
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then

        # First record has the global H1
        assert len(actual) == 4
        assert actual[0]['type'] == 'lvl0'
        assert actual[0]['hierarchy']['lvl0'] == 'Foo'
        assert actual[0]['hierarchy']['lvl1'] is None
        assert actual[0]['hierarchy']['lvl2'] is None
        assert actual[0]['content'] is None

class TestGetRecordsFromDomWithStripChars:
    def test_strip_chars(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>.Foo;</h1>
            <h2>!Bar.</h2>
            <h3>,Baz!</h3>
            <p>,text,</p>
        </body></html>
        """)

        STRATEGY.config.strip_chars = ',.'
        STRATEGY.set_selectors({
            "lvl0": "h1",
            "lvl1": "h2",
            "lvl2": "h3",
            "content": "p"
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo;'
        assert actual[3]['hierarchy']['lvl1'] == '!Bar'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz!'
        assert actual[3]['content'] == 'text'

    def test_strip_chars_with_level_override(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>.Foo;</h1>
            <h2>!Bar.</h2>
            <h3>,Baz!</h3>
            <p>,text,</p>
        </body></html>
        """)

        STRATEGY.config.strip_chars = ',.'
        STRATEGY.set_selectors({
            "lvl0": "h1",
            "lvl1": {
                "selector": "h2",
                "strip_chars": "!"
            },
            "lvl2": "h3",
            "content": "p"
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo;'
        assert actual[3]['hierarchy']['lvl1'] == 'Bar.'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz!'
        assert actual[3]['content'] == 'text'

class TestGetRecordsFromDomWithOldTestSelector:
    def test_test_selector(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
            <h1>Foo</h1>
            <h2>Bar</h2>
            <h3>Baz</h3>
            <p>text</p>
        </body></html>
        """)

        STRATEGY.config.strip_chars = ',.'
        STRATEGY.set_selectors({
            "lvl0": "h1",
            "lvl1": "h2",
            "lvl2": "h3",
            "text": "p"
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 4
        assert actual[3]['type'] == 'content'
        assert actual[3]['hierarchy']['lvl0'] == 'Foo'
        assert actual[3]['hierarchy']['lvl1'] == 'Bar'
        assert actual[3]['hierarchy']['lvl2'] == 'Baz'
        assert actual[3]['content'] == 'text'


class TestGetSettings:
    def test_get_settings(self):
        # Given
        STRATEGY.set_selectors({
            "lvl0": "h1",
            "lvl1": "h2",
            "lvl2": "h3",
            "content": "p"
        })

        # When
        settings = STRATEGY.get_index_settings()

        # Then
        expected_settings = [
                'unordered(hierarchy_radio.lvl0)',
                'unordered(hierarchy_radio.lvl1)',
                'unordered(hierarchy_radio.lvl2)',
                'unordered(hierarchy.lvl0)',
                'unordered(hierarchy.lvl1)',
                'unordered(hierarchy.lvl2)',
                'content',
                'url,anchor'
        ]

        assert settings['attributesToIndex'] == expected_settings

class TestAllowToBypassOneOrMoreLevels:
    def test_get_settings_with_one_non_searchable(self):
        # Given
        STRATEGY.set_selectors({
         "lvl0": {
             "selector": "h1",
             "searchable": False
         },
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        # When
        settings = STRATEGY.get_index_settings()

        # Then
        expected_settings = [
            'unordered(hierarchy_radio.lvl1)',
            'unordered(hierarchy_radio.lvl2)',
            'unordered(hierarchy.lvl1)',
            'unordered(hierarchy.lvl2)',
            'content',
            'url,anchor'
        ]

        assert settings['attributesToIndex'] == expected_settings

    def test_get_records_from_dom_with_empty_selector(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
         <h2>Bar</h2>
         <h3>Baz</h3>
         <p>text</p>
        </body></html>
        """)

        STRATEGY.set_selectors({
            "lvl0": "",
            "lvl1": "h2",
            "lvl2": "h3",
            "content": "p"
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 3
        assert actual[2]['type'] == 'content'
        assert actual[2]['hierarchy']['lvl0'] is None
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] == 'Baz'
        assert actual[2]['content'] == 'text'

    def test_get_records_from_dom_with_empty_selector_and_default_value(self):
        # Given
        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
         <h2>Bar</h2>
         <h3>Baz</h3>
         <p>text</p>
        </body></html>
        """)

        STRATEGY.set_selectors({
            "lvl0": {
                "selector": "",
                "default_value": "Documentation"
            },
            "lvl1": "h2",
            "lvl2": "h3",
            "content": "p"
        })

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert len(actual) == 3
        assert actual[2]['type'] == 'content'
        assert actual[2]['hierarchy']['lvl0'] == 'Documentation'
        assert actual[2]['hierarchy']['lvl1'] == 'Bar'
        assert actual[2]['hierarchy']['lvl2'] == 'Baz'
        assert actual[2]['content'] == 'text'

class TestPageRank:
    def test_default_page_rank_should_be_zero(self):
        # Given
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom()

        # Then
        assert actual[0]['weight']['page_rank'] == 0

    def test_positive_page_rank(self):
        # Given
        STRATEGY.config.start_urls = [{'url': 'http://foo.bar/api', 'page_rank': 1, 'tags': []}]
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom("http://foo.bar/api")

        # Then
        assert actual[0]['weight']['page_rank'] == 1

    def test_positive_sub_page_page_rank(self):
        # Given
        STRATEGY.config.start_urls = [{'url': 'http://foo.bar/api', 'page_rank': 1, 'tags': []}]
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom("http://foo.bar/api/test")

        # Then
        assert actual[0]['weight']['page_rank'] == 1

    def test_negative_page_rank(self):
        # Given
        STRATEGY.config.start_urls = [{'url': 'http://foo.bar/api', 'page_rank': -1, 'tags': []}]
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom("http://foo.bar/api/test")

        # Then
        assert actual[0]['weight']['page_rank'] == -1

class TestTags:
    def test_adding_tags_for_page(self):
        # Given
        STRATEGY.config.start_urls = [{'url': 'http://foo.bar/api', 'page_rank': 0, 'tags': ["test"]}]
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom("http://foo.bar/api")

        # Then
        assert actual[0]['tags'] == ["test"]

    def test_adding_tags_for_subpage(self):
        # Given
        STRATEGY.config.start_urls = [{'url': 'http://foo.bar/api', 'page_rank': 0, 'tags': ["test"]}]
        STRATEGY.set_selectors({
         "lvl0": "h1",
         "lvl1": "h2",
         "lvl2": "h3",
         "content": "p"
        })

        STRATEGY.dom = lxml.html.fromstring("""
        <html><body>
         <h1>Foo</h1>
        </body></html>
        """)

        # When
        actual = STRATEGY.get_records_from_dom("http://foo.bar/api/test")

        # Then
        assert actual[0]['tags'] == ["test"]