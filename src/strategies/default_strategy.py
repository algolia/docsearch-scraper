"""
Default Strategy
"""
from strategies.abstract_strategy import AbstractStrategy
import time

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
            if record['anchor'] != None:
                record['url'] = url + '#' + record['anchor']
            else:
                record['url'] = url


        return records

    def get_records_from_dom(self):
        if self.dom == None:
            exit('DefaultStrategy.dom is not defined')

        # We get a big selector that matches all relevant nodes, in order
        # But we also keep a list of all matches for each individual level
        levels = list(self.levels)
        levels.append('text')
        selector_all = []
        nodes_per_level = {}
        for level in levels:
            level_selector = self.config.selectors[level]
            selector_all.append(level_selector)
            nodes_per_level[level] = self.cssselect(level_selector)

        nodes = self.cssselect(",".join(selector_all))
        print len(nodes), "nodes found"


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
                    break;

            # We set the hierarchy as the same as the previous one
            # We override the current level
            # And set all levels after it to None
            hierarchy = previous_hierarchy.copy()

            # Update the hierarchy for each new header
            if current_level != 'text':
                hierarchy[current_level] = self.get_text(node)
                anchors[current_level] = self.get_anchor(node)

                current_level_int = int(current_level[3:])
                for index in range(current_level_int + 1, 6):
                    hierarchy['lvl' + str(index)] = None
                    anchors['lvl' + str(index)] = None
                previous_hierarchy = hierarchy

            # Getting the element anchor as the closest one
            anchor = None
            for index in reversed(range(6)):
                potential_anchor = anchors['lvl' + str(index)]
                if potential_anchor == None:
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
            'highlightPreTag': '<span class="ads-suggestion--highlight">',
            'highlightPostTag': '</span>',
            'minWordSizefor1Typo': 3,
            'minWordSizefor2Typos': 7,
            'allowTyposOnNumericTokens': False,
            'minProximity': 2,
            'ignorePlurals': True,
            'advancedSyntax': True,
            'removeWordsIfNoResults': 'allOptional'
        }

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

    def get_parent(self, set_element, selectors):
        """Given any element and a set of selectors, will return the closest
        hierarchical parent that matches one of the selector.
        It will check all previous siblings and previous siblings of the parent
        in order, recursively.
        Will return an object containing the matching element, and the level of
        the match"""

        # No parent selectors, so no parent to find
        if len(selectors) == 0:
            return None

        # We stop if we hit the body
        if set_element.tag == 'body':
            return None

        # We return this element if it matches
        if self.element_matches_selector(set_element, selectors):
            return {
                'lvl': self.selector_level_matched(set_element),
                'element': set_element
                }

        # Does it have children? If so, we start over from the last child
        children = set_element.getchildren()
        if len(children) > 0:
            last_child = children[-1]
            return self.get_parent(last_child, selectors)

        # Does it have a previous sibling? If so, we start over from that one
        previous = set_element.getprevious()
        if previous != None:
            return self.get_parent(previous, selectors)


        # Not found at this level. Let's go up one notch
        parent = set_element.getparent()

        # We've hit the body
        if parent.tag == 'body':
            return None

        while True:
            # Just checking if the parent matches
            if self.element_matches_selector(parent, selectors):
                return {
                    'lvl': self.selector_level_matched(parent),
                    'element': parent
                    }

            # Do we have a previous sibling of the parent?
            previous_of_parent = parent.getprevious()

            # If not, let's start again on to the next
            if previous_of_parent == None:
                parent = parent.getparent()
                continue

            # We've hit the body
            if previous_of_parent.tag == 'body':
                return None

            # We start over on the previous sibling of the parent
            return self.get_parent(previous_of_parent, selectors)

        return None


    def get_anchor(self, element):
        """
        Return a possible anchor for that element.
        Looks for name and id, and if not found will look in children
        """

        # Check the name or id on the element
        anchor = element.get('name', element.get('id'))
        if anchor != None:
            return anchor

        # Check on child
        children = element.cssselect('[name],[id]')
        if len(children) > 0:
            return children[-1].get('name', element.get('id'))

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
            if is_found == False and value != None:
                is_found = True
                hierarchy_radio[level] = value
                continue

            hierarchy_radio[level] = None

        return hierarchy_radio


    def get_hierarchy(self, element, set_level):
        """Returns the hierarchy of the record, where all levels that have
        a matching element will be filled
        Ex: {
            lvl0: Foo,
            lvl1: Bar,
            lvl2: Baz,
            lvl3: None,
            lvl4: None,
            lvl5: None
        }
        """


        # We start with a blank state
        hierarchy = {}
        for level in self.levels:
            hierarchy[level] = None
        # Adding the one we know about
        if set_level in self.levels:
            hierarchy[set_level] = self.get_text(element)

        # Finding all possible parents and adding them
        selectors = self.get_all_parent_selectors(set_level)
        while True:
            parent = self.get_parent(element, selectors)
            # No more parent to find, we can stop
            if not parent:
                return hierarchy

            # We add the found parent to the hierarchy
            found_level = parent['lvl']
            hierarchy[found_level] = self.get_text(parent['element'])

            # We update the list of selectors
            selectors = self.get_all_parent_selectors(found_level)

    def get_hierarchy_complete(self, hierarchy):
        """Returns the hierarchy complete hierarchy of the record, where each
        level includes the previous levels, separated with ">".

        Works well with the instantsearch.js hierarchicalMenu widget
        Ex: {
            lvl0: Foo,
            lvl1: Foo > Bar,
            lvl2: Foo > Bar >  Baz,
            lvl3: None,
            lvl4: None,
            lvl5: None
        }
        """
        full_content = []
        hierarchy_complete = {}
        for level in self.levels:
            content = hierarchy[level]

            if content == None:
                hierarchy_complete[level] = None
                continue

            full_content.append(content)
            hierarchy_complete[level] = " > ".join(full_content)

        return hierarchy_complete
