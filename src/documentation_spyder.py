import lxml
from lxml.cssselect import CSSSelector
import re
import itertools
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class DocumentationSpyder(CrawlSpider):
    def __init__(self, index_name, allowed_domains, start_urls, stop_urls,
                 selectors, algolia_helper, strategy, *args, **kwargs):

        self.name = index_name
        self.allowed_domains = allowed_domains
        self.start_urls = start_urls
        self.selectors = selectors
        self.algolia_helper = algolia_helper
        self.stategy = strategy

        super(DocumentationSpyder, self).__init__(*args, **kwargs)
        DocumentationSpyder.rules = [
            Rule(LxmlLinkExtractor(allow=self.start_urls, deny=stop_urls), callback="parse_item", follow=True)
        ]
        super(DocumentationSpyder, self)._compile_rules()

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
                    if self.find_matching_el(el, separate_results[selector]):
                        current_selector = i
                        break
                if current_selector != -1:
                    break
            blocs.append(((el, self.get_element_content(el)), current_selector))

        self.index_document(blocs, response)

    def index_document(self, blocs, response):
        objects = self.stategy.create_objects_from_document(blocs, response)

        print response.url
        self.algolia_helper.add_objects(objects)

    def find_matching_el(self, el, l):
        for elem in l:
            if el.getroottree().getpath(el) == elem.getroottree().getpath(elem):
                return True
        return False

    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s += re.sub('\s+', ' ', x.strip(' \t\n\r'))

        return s
