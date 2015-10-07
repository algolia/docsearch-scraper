import lxml
from lxml.cssselect import CSSSelector
import re
import copy
import itertools
from urlparse import urlparse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class DocumentationSpyder(CrawlSpider):
    def __init__(self, index_name, allowed_domains, start_urls, stop_urls, selectors, algolia_helper,  *args, **kwargs):
        self.name = index_name
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.selectors = selectors
        self.algolia_helper = algolia_helper

        super(DocumentationSpyder, self).__init__(*args, **kwargs)
        DocumentationSpyder.rules = [
            Rule(LxmlLinkExtractor(allow=self.start_urls, deny=stop_urls), callback="parse_item", follow=True)
        ]
        super(DocumentationSpyder, self)._compile_rules()

    def get_results(self):
        return self.arrays

    def parse_item(self, response):
        if not "text/html" in response.headers['Content-Type']:
            return

        self.scrap_content(response)

    def scrap_content(self, response):
        doc = lxml.html.fromstring(response.body)

        separate_results = {}

        for selector_group in self.selectors:
            for selector in selector_group:
                separate_selector = CSSSelector(selector)
                separate_results[selector] = separate_selector(doc)

        sel = CSSSelector(','.join(list(itertools.chain(*self.selectors))))

        blocs = []

        for el in sel(doc):
            current_selector = -1
            for i, selector_group in enumerate(self.selectors):
                for selector in selector_group:
                    if self.findMatchingElem(el, separate_results[selector]):
                        current_selector = i
                        break
                if current_selector != -1:
                    break
            blocs.append(((el, self.get_element_content(el)), current_selector))

        self.index_document(blocs, response)

    def get_key(self, i):
        if i == 0:
            return 'title'
        if i == (len(self.selectors) - 1):
            return 'content'
        return 'h' + str(i)

    def index_document(self, blocs, response):
        objects = []
        current_blocs = {}

        for i in range(0, len(self.selectors)):
            current_blocs[self.get_key(i)] = None

        for ((el, bloc), importance) in blocs:
            for i in range(importance, len(self.selectors)):
                current_blocs[self.get_key(i)] = None

            current_blocs[self.get_key(importance)] = bloc
            current_blocs['importance'] = self.get_importance(current_blocs)
            current_blocs['link'] = response.url + self.get_hash(el)
            current_blocs['hash'] = self.get_hash(el)
            current_blocs['path'] = urlparse(current_blocs['link']).path

            objects.append(copy.deepcopy(current_blocs))

        print response.url
        self.algolia_helper.add_objects(objects)

    def get_hash(self, el):
        current_el = el

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        while current_el.getprevious() is not None and current_el.get('id', default=None) is None:
            current_el = current_el.getprevious()

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        while current_el.getparent() is not None and current_el.get('id', default=None) is None:
            current_el = current_el.getparent()

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        return ""

    def get_importance(self, current_blocs):
        importance = -1
        for i in range(0, len(self.selectors)):
            if current_blocs.get(self.get_key(i)) is not None:
                importance += 1

        return importance

    def findMatchingElem(self, el, l):
        for elem in l:
            if el.getroottree().getpath(el) == elem.getroottree().getpath(elem):
                return True
        return False

    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s += re.sub('\s+', ' ', x.strip(' \t\n\r'))

        return s