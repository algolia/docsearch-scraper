from cssselect import HTMLTranslator
from lxml.cssselect import CSSSelector
from lxml.etree import XPath
import lxml
import re
import json

"""
Abstract Strategy
"""


class AbstractStrategy(object):
    """
    Abstract Strategy
    """
    config = None

    def __init__(self, config):
        self.config = config

    @staticmethod
    def pprint(data):
        """Pretty print a JSON-like structure"""
        print json.dumps(data, indent=2, sort_keys=True)

    @staticmethod
    def get_dom(response):
        """Get the DOM representation of the webpage"""
        try:
            body = response.body.decode(response.encoding)
        except UnicodeError:
            body = response.body

        return lxml.html.fromstring(body)

    def get_strip_chars(self, level):
        if self.config.selectors[level]['strip_chars'] is None:
            return self.config.strip_chars
        return self.config.selectors[level]['strip_chars']

    @staticmethod
    def get_text(element, strip_chars=None):
        """Return the text content of a DOM node"""
        text = element

        # Do not call text_content if not needed (Ex. xpath selector with text() doesn't return a node but a string)
        if not isinstance(text, basestring):
            text = text.text_content()

        # We call strip a first time for space, tab, newline, return and formfeed
        text = text.strip()
        # then one more time if with custom strip_chars if there is some
        if strip_chars is not None:
            text = text.strip(strip_chars)

        if len(text) == 0:
            return None

        return text

    @staticmethod
    def get_text_from_nodes(elements, strip_chars=None):
        """Return the text content of a set of DOM nodes"""

        if len(elements) == 0:
            return None

        text = ' '.join([AbstractStrategy.get_text(element, strip_chars) for element in elements
                         if AbstractStrategy.get_text(element, strip_chars) is not None])

        if len(text) == 0:
            return None

        return text

    @staticmethod
    def remove_from_dom(dom, exclude_selectors):
        """Remove any elements matching the selector from the DOM"""
        for selector in exclude_selectors:
            matches = CSSSelector(selector)(dom)
            if len(matches) == 0:
                continue

            for match in matches:
                match.getparent().remove(match)

        return dom

    @staticmethod
    def elements_are_equals(el1, el2):
        """Checks if two elements are actually the same"""
        return el1.getroottree().getpath(el1) == el2.getroottree().getpath(el2)

    @staticmethod
    def get_level_weight(level):
        """
        Returns a numeric weight based on the level of the selector

        >>> self.get_level_weight('lvl0') = 100
        >>> self.get_level_weight('lvl3') = 70
        >>> self.get_level_weight('content') = 0
        """
        matches = re.match(r'lvl([0-9]*)', level)
        if matches:
            return 100 - int(matches.group(1)) * 10
        return 0

    @staticmethod
    def css_to_xpath(css):
        return HTMLTranslator().css_to_xpath(css) if len(css) > 0 else ""

    def select(self, path):
        """Select an element in the current DOM using specified CSS selector"""
        return XPath(path)(self.dom) if len(path) > 0 else []

    def get_index_settings(self):
        raise Exception('get_index_settings need to be implemented')

    def get_records_from_response(self):
        raise Exception('get_records_from_response need to be implemented')
