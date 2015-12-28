"""
Default Strategy
"""
from strategies.abstract_strategy import AbstractStrategy

class DefaultStrategy(AbstractStrategy):
    """
    DefaultStrategy
    """
    dom = None

    def __init__(self, config):
        super(DefaultStrategy, self).__init__(config)
        self.levels = ['lvl0', 'lvl1', 'lvl2', 'lvl3', 'lvl4', 'lvl5']

    def get_records_from_response(self, response):
        """
        Main method called from the DocumentationSpider. Will be passed the HTTP
        response and will return a list of all records"""
        self.dom = self.get_dom(response)
        self.dom = self.remove_from_dom(self.dom, self.config.selectors_exclude)

        url = response.url

        records = self.get_records_from_dom()

        # Add page-related attributes to the records
        for record in records:
            if record['anchor'] is not None:
                record['url'] = url + '#' + record['anchor']
            else:
                record['url'] = url

        return records

    def get_records_from_dom(self):
        if self.dom is None:
            exit('DefaultStrategy.dom is not defined')

        # We get a big selector that matches all relevant nodes, in order
        # But we also keep a list of all matches for each individual level
        levels = list(self.levels)

        used_levels = []

        # Because all levels might not be used we check if the level is present in the config
        for level in levels:
            if level not in self.config.selectors:
                break
            used_levels.append(level)
        if 'text' in self.config.selectors:
            used_levels.append('text')
        levels = used_levels

        selector_all = []
        nodes_per_level = {}
        for level in levels:
            level_selector = self.config.selectors[level]
            selector_all.append(level_selector)
            nodes_per_level[level] = self.cssselect(level_selector)

        nodes = self.cssselect(",".join(selector_all))

        # We keep the current hierarchy and anchor state between loops
        previous_hierarchy = {}
        anchors = {}
        for index in range(6):
            previous_hierarchy['lvl' + str(index)] = None
            anchors['lvl' + str(index)] = None

        records = []
        for position, node in enumerate(nodes):
            # Which level is the selector matching?
            for level in levels:
                if node in nodes_per_level[level]:
                    current_level = level
                    break

            # We set the hierarchy as the same as the previous one
            # We override the current level
            # And set all levels after it to None
            hierarchy = previous_hierarchy.copy()

            # Update the hierarchy for each new header
            current_level_int = int(current_level[3:]) if current_level != 'text' else 6 # 6 > lvl5
            if current_level != 'text':
                hierarchy[current_level] = self.get_text(node)
                anchors[current_level] = self.get_anchor(node)

                for index in range(current_level_int + 1, 6):
                    hierarchy['lvl' + str(index)] = None
                    anchors['lvl' + str(index)] = None
                previous_hierarchy = hierarchy

            if current_level_int < self.config.min_indexed_level:
                continue

            # Getting the element anchor as the closest one
            anchor = None
            for index in reversed(range(6)):
                potential_anchor = anchors['lvl' + str(index)]
                if potential_anchor is None:
                    continue
                anchor = potential_anchor
                break

            # We only save content for the 'text' matches
            content = None if current_level != 'text' else self.get_text(node)
            hierarchy_radio = self.get_hierarchy_radio(hierarchy)
            hierarchy_complete = self.get_hierarchy_complete(hierarchy)
            weight = {
                'level': self.get_level_weight(current_level),
                'position': position
            }

            records.append({
                'anchor': anchor,
                'content': content,
                'hierarchy': hierarchy,
                'hierarchy_radio': hierarchy_radio,
                'hierarchy_complete': hierarchy_complete,
                'weight': weight,
                'type': current_level
            })

        return records

    def get_index_settings(self):
        settings = {
            'attributesToIndex': [
                # We first look for matches in the exact titles
                'unordered(hierarchy_radio.lvl0)',
                'unordered(hierarchy_radio.lvl1)',
                'unordered(hierarchy_radio.lvl2)',
                'unordered(hierarchy_radio.lvl3)',
                'unordered(hierarchy_radio.lvl4)',
                'unordered(hierarchy_radio.lvl5)',
                # Then in the whole title hierarchy
                'unordered(hierarchy.lvl0)',
                'unordered(hierarchy.lvl1)',
                'unordered(hierarchy.lvl2)',
                'unordered(hierarchy.lvl3)',
                'unordered(hierarchy.lvl4)',
                'unordered(hierarchy.lvl5)',
                # And only in textual content at the end
                'content',
                # And really, we can still have a look in those as well...
                'url,anchor'
            ],
            'attributesToRetrieve': [
                'hierarchy',
                'content',
                'anchor',
                'url'
            ],
            'attributesToHighlight': [
                'hierarchy',
                'content'
            ],
            'attributesToSnippet': [
                'content:10'
            ],
            'distinct': True,
            'attributeForDistinct': 'url',
            # TODO: Allow passing custom weight to pages through the config
            'customRanking': [
                'desc(weight.level)',
                'desc(weight.position)'
            ],
            # Default ranking is: typo, geo, words, proximity, attribute, exact, custom
            # - We removed geo as this is irrelevant
            # - We moved words before typo, because in case of a documentation
            #   search you have no idea where your matching words will be (not
            #   necessarily at the start)
            # - For the same reason, we put proximity lower and gave more weight
            #   to attribute
            'ranking': [
                'words',
                'typo',
                'attribute',
                'proximity',
                'exact',
                'custom'
            ],
            'highlightPreTag': '<span class="algolia-docsearch-suggestion--highlight">',
            'highlightPostTag': '</span>',
            'minWordSizefor1Typo': 3,
            'minWordSizefor2Typos': 7,
            'allowTyposOnNumericTokens': False,
            'minProximity': 2,
            'ignorePlurals': True,
            'advancedSyntax': True,
            'removeWordsIfNoResults': 'allOptional'
        }

        # apply custom updates
        if self.config.custom_settings is not None:
            settings.update(self.config.custom_settings)

        return settings

    def get_all_parent_selectors(self, set_level):
        """Returns a large selector that contains all the selectors for all the
        levels above the specified one"""
        parent_selectors = []
        for level in self.levels:
            if level == set_level:
                break
            parent_selectors.append(self.config.selectors[level])
        return ",".join(parent_selectors)

    def selector_level_matched(self, set_element):
        """Returns which selector level this element is matching"""
        levels = list(self.levels)
        levels.append('text')
        for level in levels:
            matches = self.cssselect(self.config.selectors[level])
            for match in matches:
                if self.elements_are_equals(match, set_element):
                    return level
        return False

    @staticmethod
    def get_anchor_string_from_element(element):
        return element.get('name', element.get('id'))

    def get_anchor(self, element):
        """
        Return a possible anchor for that element.
        Looks for name and id, and if not found will look in children
        """

        # Check the name or id on the element
        anchor = self.get_anchor_string_from_element(element)

        if anchor is not None:
            return anchor

        # Check on child
        children = element.cssselect('[name],[id]')
        if len(children) > 0:
            return self.get_anchor_string_from_element(children[-1])

        el = element

        while el is not None:
            # go back
            while el.getprevious() is not None:
                el = el.getprevious()

                if el is not None:
                    anchor = self.get_anchor_string_from_element(el)

                    if anchor is not None:
                        return anchor

            # check last previous
            if el is not None:
                anchor = self.get_anchor_string_from_element(el)

                if anchor is not None:
                    return anchor

            # go up
            el = el.getparent()

            if el is not None:
                anchor = self.get_anchor_string_from_element(el)

                # check parent
                if anchor is not None:
                    return anchor

        # No more parent, we have no anchor
        return None

    def get_hierarchy_radio(self, hierarchy):
        """Returns the radio hierarchy for the record, where only one level is
        filled and the others are empty
        Ex: {
            lvl0: None,
            lvl1: None,
            lvl2: Baz,
            lvl3: None,
            lvl4: None,
            lvl5: None
        }
        """

        hierarchy_radio = {}
        is_found = False
        for level in reversed(self.levels):
            value = hierarchy[level]
            if is_found is False and value is not None:
                is_found = True
                hierarchy_radio[level] = value
                continue

            hierarchy_radio[level] = None

        return hierarchy_radio

    def get_hierarchy_complete(self, hierarchy):
        """Returns the hierarchy complete hierarchy of the record, where each
        level includes the previous levels, separated with ">".

        Works well with the instantsearch.js hierarchicalMenu widget
        Ex: {
            lvl0: Foo,
            lvl1: Foo > Bar,
            lvl2: Foo > Bar > Baz,
            lvl3: None,
            lvl4: None,
            lvl5: None
        }
        """
        full_content = []
        hierarchy_complete = {}
        for level in self.levels:
            content = hierarchy[level]

            if content is None:
                hierarchy_complete[level] = None
                continue

            full_content.append(content)
            hierarchy_complete[level] = " > ".join(full_content)

        return hierarchy_complete
