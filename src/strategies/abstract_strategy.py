from lxml.cssselect import CSSSelector
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
        self.config.selectors = self.parse_selectors(self.config.selectors)

    def set_selectors(self, selectors):
        self.config.selectors = self.parse_selectors(selectors)

    @staticmethod
    def parse_selectors(config_selectors):
        selectors = {}

        for key in config_selectors:
            selectors[key] = config_selectors[key]

            # Backward compatibility, if it's a string then we put it in an object
            if isinstance(selectors[key], basestring):
                selectors[key] = {'selector': selectors[key]}

            if 'global' in selectors[key]:
                selectors[key]['global'] = bool(selectors[key]['global'])
            else:
                selectors[key]['global'] = False

        return selectors

    @staticmethod
    def pprint(data):
        """Pretty print a JSON-like structure"""
        print json.dumps(data, indent=2, sort_keys=True)

    @staticmethod
    def get_dom(response):
        """Get the DOM representation of the webpage"""
        try:
            body = response.body.decode(response.encoding)
        except UnicodeDecodeError:
            body = response.body

        return lxml.html.fromstring(body)

    @staticmethod
    def get_text(element):
        """Return the text content of a DOM node"""
        return element.text_content().strip()

    @staticmethod
    def get_text_from_nodes(elements):
        """Return the text content of a set of DOM nodes"""
        return ' '.join([element.text_content().strip() for element in elements])

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
        >>> self.get_level_weight('text') = 0
        """
        matches = re.match(r'lvl([0-9]*)', level)
        if matches:
            return 100 - int(matches.group(1)) * 10
        return 0

    def element_matches_selector(self, set_element, selectors):
        """Returns true if `element` matches at least one of the selectors"""
        if len(selectors) == 0:
            return False
        # We get all the elements in the page that matches the selector and see
        # if the given one is in the list
        all_matches = self.cssselect(selectors)
        for match in all_matches:
            if self.elements_are_equals(match, set_element):
                return True

        return False

    def cssselect(self, selector):
        """Select an element in the current DOM using speficied CSS selector"""
        return CSSSelector(selector)(self.dom)

    def get_index_settings(self):
        raise Exception('get_index_settings need to be implemented')

    def get_records_from_response(self):
        raise Exception('get_records_from_response need to be implemented')
