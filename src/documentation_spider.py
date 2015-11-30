"""
DocumentationSpider
"""
from lxml.cssselect import CSSSelector
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import itertools
import lxml
import re
import pprint

class DocumentationSpider(CrawlSpider):
    """
    DocumentationSpider
    """
    def __init__(self, index_name, allowed_domains, start_urls, stop_urls,
                 selectors, selectors_exclude, strip_chars, algolia_helper, strategy, *args, **kwargs):

        self.name = index_name
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.selectors = selectors
        self.selectors_exclude = selectors_exclude
        self.strip_chars = strip_chars
        self.algolia_helper = algolia_helper
        self.stategy = strategy

        self.levels = ['lvl0','lvl1','lvl2','lvl3','lvl4','lvl5']

        # self.page_ranks = [] # order matters so array
        # self.tags = []  # order matters so array
        # self.extract_page_rank()
        # self.extract_tags()

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow=self.start_urls,
            deny=stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src')
        )
        DocumentationSpider.rules = [
            Rule(link_extractor, callback="callback", follow=True)
        ]
        super(DocumentationSpider, self)._compile_rules()

    # def extract_page_rank(self):
    #     pattern = re.compile('(.+?)(?:(?:\[page_rank:(.+?)])|(?:\[tags:(?:.+?)]))+')
    #     for url in self.start_urls:
    #         r = pattern.search(url)
    #         if r is not None and r.group(2) is not None:
    #             if r.group(2).isnumeric():
    #                 self.page_ranks.append((r.group(1), int(r.group(2))))
    #             else:
    #                 print "Non numeric page rank found `" + r.group(2) + "` for url `" + r.group(1) + "`"

    # def extract_tags(self):
    #     pattern = re.compile('(.+?)(?:(?:\[tags:(.+?)])|(?:\[page_rank:(?:.+?)]))+')
    #     for url in self.start_urls:
    #         r = pattern.search(url)
    #         if r is not None:
    #             if r.group(2) is not None:
    #                 self.tags.append((r.group(1), r.group(2).split(',')))
    #             self.start_urls[self.start_urls.index(url)] = r.group(1)

    def close(self):
        raise CloseSpider('CLOSE')

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
    

    def get_all_parent_selectors(self, set_level):
        """Returns a large selector that contains all the selectors for all the
        levels above the specified one"""
        parent_selectors = []
        for level in self.levels:
            if level == set_level:
                break
            parent_selectors.append(self.selectors[level])
        return ",".join(parent_selectors)

    def element_matches_selector(self, dom, set_element, selectors):
        """Returns true if `element` matches at least one of the selectors"""
        if len(selectors) == 0:
            return False
        # We get all the elements in the page that matches the selector and see
        # if the given one is in the list
        all_matches = CSSSelector(selectors)(dom)
        for match in all_matches:
            if self.elements_are_equals(match, set_element):
                return True

        return False

    def selector_level_matched(self, dom, set_element):
        """Returns which selector level this element is matching"""
        for level in self.levels:
            matches = CSSSelector(self.selectors[level])(dom)
            for match in matches:
                if self.elements_are_equals(match, set_element):
                    return level
        return False

    # TODO: This one totally need TESTS. It is a huge recursive beast of HTML
    # traversing with way too many layers to be left without a test harness.
    def get_parent(self, dom, set_element, selectors):
        """Given any element and a set of selectors, will return the closest
        hierarchical parent that matches one of the selector.
        It will check all previous siblings and previous siblings of the parent
        in order, recursively.
        Will return an object containing the matching element, and the level of
        the match"""

        # No parent selectors, so no parent to find
        if len(selectors) == 0:
            return False

        # We stop if we hit the body
        if set_element.tag == 'body':
            return False

        # We return this element if it matches
        if self.element_matches_selector(dom, set_element, selectors):
            return {
                'lvl': self.selector_level_matched(dom, set_element),
                'element': set_element
                }

        # Does it have children? If so, we start over from the last child
        children = set_element.getchildren()
        if len(children) > 0:
            last_child = children[-1]
            return self.get_parent(dom, last_child, selectors)

        # Does it have a previous sibling? If so, we start over from that one
        previous = set_element.getprevious()
        if previous != None:
            return self.get_parent(dom, previous, selectors)


        # Not found at this level. Let's go up one notch
        parent = set_element.getparent()
        while True:
            # Just checking if the parent matches
            if self.element_matches_selector(dom, parent, selectors):
                return {
                    'lvl': self.selector_level_matched(dom, parent),
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
                return False

            # We start over on the previous sibling of the parent
            return self.get_parent(dom, previous_of_parent, selectors)

        return False









    def get_hierarchy_radio(self, content, set_level):
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
        for level in self.levels:
            value = content if (level == set_level) else None
            hierarchy_radio[level] = value

        return hierarchy_radio

    def get_hierarchy(self, dom, element, set_level):
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
        hierarchy[set_level] = self.get_text(element)

        # Finding all possible parents and adding them
        selectors = self.get_all_parent_selectors(set_level)
        while True:
            parent = self.get_parent(dom, element, selectors)
            # No more parent to find, we can stop
            if not parent:
                return hierarchy

            # We add the found parent to the hierarchy
            found_level = parent['lvl']
            hierarchy[found_level] = self.get_text(parent['element'])

            # We update the list of selectors
            selectors = self.get_all_parent_selectors(found_level)



    def callback(self, response):
        """Callback fired on each page scrapped"""
        if "text/html" not in response.headers['Content-Type']:
            return

        self.scrap_content(response)

    def scrap_content(self, response):
        dom = self.get_dom(response)
        dom = self.remove_from_dom(dom, self.selectors_exclude)

        records = []

        for level in self.levels:
            # This level is not configured
            if not level in self.selectors:
                continue

            # Getting record content for each matching CSS selector
            matches = CSSSelector(self.selectors[level])(dom)
            for match in matches:
                content = self.get_text(match)
                hierarchy = self.get_hierarchy(dom, match, level)
                hierarchy_radio = self.get_hierarchy_radio(content, level)
                records.append({
                    # 'url':
                    # 'hierarchy_complete':
                    # weight
                    # tags
                    # anchor
                    'content': content,
                    'hierarchy': hierarchy,
                    'hierarchy_radio': hierarchy_radio,
                    'type': level
                })

            pprint.pprint(records)

        self.close()



    # def index_document(self, blocs, response):
    #     objects = self.stategy.create_objects_from_document(blocs, response, self.tags, self.page_ranks)

    #     print response.url

    #     for i in xrange(0, len(objects), 50):
    #         self.algolia_helper.add_objects(objects[i:i + 50])
