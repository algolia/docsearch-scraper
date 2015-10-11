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

        self.tags = []  # order matters so array instead of dict
        self.extract_tags()

        super(DocumentationSpyder, self).__init__(*args, **kwargs)
        DocumentationSpyder.rules = [
            Rule(LxmlLinkExtractor(allow=self.start_urls, deny=stop_urls), callback="parse_item", follow=True)
        ]
        super(DocumentationSpyder, self)._compile_rules()

    def extract_tags(self):
        pattern = re.compile('(.+)\[\[(.+?)]]')
        for url in self.start_urls:
            r = pattern.search(url)
            if r is not None:
                self.tags.append((r.group(1), r.group(2).split(',')))
                self.start_urls[self.start_urls.index(url)] = r.group(1)

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
        objects = self.stategy.create_objects_from_document(blocs, response, self.tags)

        print response.url

        for i in xrange(0, len(objects), 100):
            self.algolia_helper.add_objects(objects[i:i + 100])

    def find_matching_el(self, el, l):
        for elem in l:
            if el.getroottree().getpath(el) == elem.getroottree().getpath(elem):
                return True
        return False

    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s += ' ' + x.strip(' \t\n\r')

        return re.sub('\s+', ' ', s.strip(' :;,.'))
