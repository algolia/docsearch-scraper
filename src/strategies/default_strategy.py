"""
Default Strategy
"""
from strategies.abstract_strategy import AbstractStrategy
from lxml.cssselect import CSSSelector

class DefaultStrategy(AbstractStrategy):
    """
    DefaultStrategy
    """

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

        records = []

        # Getting the records of the hierarchy
        levels = list(self.levels)
        levels.append('text')
        for level in levels:
            # This level is not configured
            if not level in self.config.selectors:
                continue

            # Getting record content for each matching CSS selector
            matches = self.cssselect(self.config.selectors[level])
            for position, match in enumerate(matches):
                content = self.get_text(match)
                hierarchy = self.get_hierarchy(match, level)
                hierarchy_radio = self.get_hierarchy_radio(hierarchy)
                hierarchy_complete = self.get_hierarchy_complete(hierarchy)
                anchor = self.get_anchor(match, level)
                weight = {
                    'level': self.get_level_weight(level),
                    'position': position
                }

                records.append({
                    'url': url,
                    'anchor': anchor,
                    'content': content,
                    'hierarchy': hierarchy,
                    'hierarchy_radio': hierarchy_radio,
                    'hierarchy_complete': hierarchy_complete,
                    'weight': weight,
                    'type': level
                })

        self.pprint(records)

        return records



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
        for level in self.levels:
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


    def get_anchor(self, element, level):
        """Return the closest #anchor to access this element.
        Will be the element name or id if one is set, otherwise will go up the
        three of all parents"""

        # Check the name or id on the element
        anchor = element.get('name', element.get('id'))
        if anchor != None:
            return anchor

        # Check on child
        children = element.cssselect('[name],[id]')
        if len(children) > 0:
            return children[-1].get('name', element.get('id'))

        # Not found at this level, we try again at the parent level
        all_parent_selectors = self.get_all_parent_selectors(level)
        parent = self.get_parent(element, all_parent_selectors)
        if parent != None:
            return self.get_anchor(parent['element'], parent['lvl'])

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









# def get_settings(self):
#     print "kjkkjkjk"

# attributes_to_index = ['unordered(text_title)']
# attributes_to_highlight = ['title']
# attributes_to_retrieve = ['title']

# Add 



# print self.config.selectors
# print self.selectors

# TODO: This part adds all the hX to the settings
# We'll need to redo it with hierarchy.lvl0, hierarchy.lvl1
#
# hierarchicalFacet (avec chaque niveau qui contient le niveau previous
# hierarchy (0, 1, 2, 3, 4), to have a real hierarchy where each key is
# filled is there is something
# hierarchy_unique, where only the matching level is filled and the
# other are nil
# hierarchy_html for the hierarchy with html ontent
#
#
# for i in range(1, len(self.config.get_selectors()) - 1):
#     attributes_to_index.append('unordered(text_h' + str(i) + ')')

# attributes_to_index.append('unordered(title)')

# for i in range(1, len(self.config.get_selectors()) - 1):
#     attributes_to_index.append('unordered(h' + str(i) + ')')
#     attributes_to_highlight.append('h' + str(i))
#     attributes_to_retrieve.append('h' + str(i))

# attributes_to_index += ['content', 'path', 'hash']
# attributes_to_highlight += ['content']
# attributes_to_retrieve += ['_tags', 'link']

# settings = {
#     'attributesToIndex'         : attributes_to_index,
#     'attributesToHighlight'     : attributes_to_highlight,
#     'attributesToRetrieve'      : attributes_to_retrieve,
#     'attributesToSnippet'       : ['content:50'],
#     'customRanking'             : ['desc(page_rank)', 'asc(importance)', 'asc(nb_words)'],
#     'ranking'                   : ['words', 'typo', 'attribute', 'proximity', 'exact', 'custom'],
#     'minWordSizefor1Typo'       : 3,
#     'minWordSizefor2Typos'      : 7,
#     'allowTyposOnNumericTokens' : False,
#     'minProximity'              : 2,
#     'ignorePlurals'             : True,
#     'advancedSyntax'            : True,
#     'removeWordsIfNoResults'    : 'allOptional'
# }

# settings.update(self.custom_settings)

# return settings


