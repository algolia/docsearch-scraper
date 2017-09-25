"""
Default Strategy
"""

import re
import json

from .abstract_strategy import AbstractStrategy
from .anchor import Anchor
from .hierarchy import Hierarchy
from ..config.urls_parser import UrlsParser


class DefaultStrategy(AbstractStrategy):
    """
    DefaultStrategy
    """
    dom = None

    def __init__(self, config):
        super(DefaultStrategy, self).__init__(config)
        self.levels = ['lvl0', 'lvl1', 'lvl2', 'lvl3', 'lvl4', 'lvl5', 'lvl6']
        self.global_content = {}
        self.page_rank = {}

    def get_records_from_response(self, response):
        """
        Main method called from the DocumentationSpider. Will be passed the HTTP
        response and will return a list of all records"""

        if self._body_contains_stop_content(response):
            return []

        self.dom = self.get_dom(response)
        self.dom = self.remove_from_dom(self.dom, self.config.selectors_exclude)

        records = self.get_records_from_dom(response.url)

        return records

    def _update_hierarchy_with_global_content(self, hierarchy, current_level_int):
        for index in range(0, current_level_int + 1):
            if 'lvl' + str(index) in self.global_content:
                hierarchy['lvl' + str(index)] = self.global_content['lvl' + str(index)]

        return hierarchy

    def get_records_from_dom(self, current_page_url=None):

        if self.dom is None:
            exit('DefaultStrategy.dom is not defined')

        # Reset it to be able to have a clean instance when testing
        self.global_content = {}

        selectors = self.get_selectors_set(current_page_url)
        levels = self._get_used_levels(selectors)

        # We get a big selector that matches all relevant nodes, in order
        # But we also keep a list of all matches for each individual level
        nodes_per_level = self._get_nodes_per_level(selectors, levels)
        nodes = self._get_all_matching_nodes(levels, selectors)

        # We keep the current hierarchy and anchor state between loops
        previous_hierarchy = self._generate_empty_hierarchy()
        anchors = self._generate_empty_hierarchy()

        records = []

        for position, node in enumerate(nodes):
            current_level = self._get_level_of_node(node, nodes_per_level, levels)

            # If the current node is part of a global level it's possible
            # that it doesn't match because we take only one node for global selectors
            if current_level is None:
                continue

            # We copy the previous hierarchy, We override the current level, And set all levels after it to None
            hierarchy = previous_hierarchy.copy()

            # Update the hierarchy for each new header
            current_level_int = levels.index(current_level)

            if current_level != 'content':
                hierarchy[current_level] = self._get_text_content_for_level(node, current_level, selectors)
                anchors[current_level] = Anchor.get_anchor(node)

                for index in range(current_level_int + 1, 7):
                    hierarchy['lvl' + str(index)] = None
                    anchors['lvl' + str(index)] = None
                previous_hierarchy = hierarchy

            if current_level_int < self.get_min_indexed_level_for_url(current_page_url):
                continue

            hierarchy = self._update_hierarchy_with_global_content(hierarchy, current_level_int)

            # We only save content for the 'text' matches
            content = None if current_level != 'content' else self.get_text(node, self.get_strip_chars(current_level, selectors))

            hierarchy, content = self._handle_default_values(hierarchy, content, selectors)

            # noinspection PyDictCreation
            record = {
                'anchor': self._get_closest_anchor(anchors),
                'content': content,
                'hierarchy': hierarchy,
                'hierarchy_radio': Hierarchy.get_hierarchy_radio(hierarchy, current_level, levels),
                'type': current_level,
                'tags': UrlsParser.get_tags(current_page_url, self.config.start_urls),
                "extra_attributes": UrlsParser.get_extra_attributes(current_page_url, self.config.start_urls),
                'weight': {
                    'page_rank': UrlsParser.get_page_rank(current_page_url, self.config.start_urls),
                    'level': self.get_level_weight(current_level),
                    'position': position
                },
                'url': current_page_url,
                'url_without_variables': current_page_url
            }

            record['hierarchy_camel'] = record['hierarchy'],
            record['hierarchy_radio_camel'] = record['hierarchy_radio']
            record['content_camel'] = record['content']

            # get meta data
            for meta_node in self.select('//meta'):
                name = meta_node.get('name')
                content = meta_node.get('content')
                if name and name.startswith('docsearch:') and content:
                    name = name.replace('docsearch:', '')
                    record[name] = json.loads(content)

            if current_page_url is not None:
                # Add variables to the record
                for attr, value, url_without_variables in UrlsParser.get_url_variables(current_page_url, self.config.start_urls):
                    record['url_without_variables'] = url_without_variables
                    record[attr] = value

                record['url_without_anchor'] = record['url']
                record['url'] = self._get_url_with_anchor(record['url'], record['anchor'])
                record['url_without_variables'] = self._get_url_with_anchor(record['url_without_variables'], record['anchor'])
                record['no_variables'] = record['url'] == record['url_without_variables']

            records.append(record)

        return records

    def _get_text_content_for_level(self, node, current_level, selectors):
        if 'attributes' in selectors[current_level]:
            attributes = {}
            for attribute_name in selectors[current_level]['attributes'].keys():
                matching_nodes = node.xpath(selectors[current_level]['attributes'][attribute_name]['selector'])
                attributes[attribute_name] = self.get_text_from_nodes(
                    matching_nodes,
                    self.get_strip_chars(attribute_name, selectors[current_level]['attributes'])
                )
            return attributes

        if current_level in self.global_content:
            return self.global_content[current_level]

        return self.get_text(node, self.get_strip_chars(current_level, selectors))

    @staticmethod
    def _get_closest_anchor(anchors):
        # Getting the element anchor as the closest one
        for index in reversed(range(7)):
            potential_anchor = anchors['lvl' + str(index)]
            if potential_anchor is None:
                continue
            return potential_anchor

        return None

    @staticmethod
    def _generate_empty_hierarchy():
        return {
            "lvl0": None,
            "lvl1": None,
            "lvl2": None,
            "lvl3": None,
            "lvl4": None,
            "lvl5": None,
            "lvl6": None,
        }

    @staticmethod
    def _get_level_of_node(node, nodes_per_level, levels):
        for level in levels:
            if node in nodes_per_level[level]:
                return level

        return None

    @staticmethod
    def _handle_default_values(hierarchy, content, selectors):
        # Handle default values
        for level in selectors:
            if level != 'content':
                if hierarchy[level] is None and selectors[level]['default_value'] is not None:
                    hierarchy[level] = selectors[level]['default_value']
            else:
                if content is None and selectors[level]['default_value'] is not None:
                    content = selectors['content']['default_value']

        return hierarchy, content

    def _get_nodes_per_level(self, selectors, levels):
        nodes_per_level = {}

        for level in levels:
            level_selector = selectors[level]
            matching_dom_nodes = self.select(level_selector['selector'])

            if not level_selector['global']:
                nodes_per_level[level] = matching_dom_nodes
            else:
                self.global_content[level] = self.get_text_from_nodes(matching_dom_nodes, self.get_strip_chars(level, selectors))
                # We only want 1 record
                nodes_per_level[level] = [matching_dom_nodes[0]] if len(matching_dom_nodes) > 0 else []

        return nodes_per_level

    def _get_all_matching_nodes(self, levels, selectors):
        return self.select(" | ".join(self._get_selector_all(levels, selectors)))

    @staticmethod
    def _get_selector_all(levels, selectors):
        selector_all = []
        for level in levels:
            level_selector = selectors[level]

            if len(level_selector['selector']) > 0:
                selector_all.append(level_selector['selector'])

        return selector_all

    def _get_used_levels(self, selectors):
        levels = list(self.levels)

        used_levels = []

        for level in levels:
            if level not in selectors:
                break
            used_levels.append(level)

        if 'content' in selectors:
            used_levels.append('content')

        return used_levels

    def _body_contains_stop_content(self, response):
        if len(self.config.stop_content) > 0:
            body = self.get_body(response)

            for stop_content in self.config.stop_content:
                if stop_content in body:
                    return True

        return False

    def _get_url_with_anchor(self, current_page_url, anchor):
        if (not self.config.js_render or not self.config.use_anchors) and anchor is not None:
            return current_page_url + '#' + anchor

        return current_page_url
