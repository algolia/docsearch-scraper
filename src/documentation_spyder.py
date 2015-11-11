import lxml
from lxml.cssselect import CSSSelector
import re
import itertools
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class DocumentationSpyder(CrawlSpider):
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

        self.page_ranks = [] # order matters so array
        self.tags = []  # order matters so array
        self.extract_page_rank()
        self.extract_tags()

        super(DocumentationSpyder, self).__init__(*args, **kwargs)
        DocumentationSpyder.rules = [
            Rule(LxmlLinkExtractor(allow=self.start_urls, deny=stop_urls, tags=('a', 'area', 'iframe'), attrs=('href', 'src')),
                callback="parse_item", follow=True)
        ]
        super(DocumentationSpyder, self)._compile_rules()

    def extract_page_rank(self):
        pattern = re.compile('(.+?)(?:(?:\[page_rank:(.+?)])|(?:\[tags:(?:.+?)]))+')
        for url in self.start_urls:
            r = pattern.search(url)
            if r is not None and r.group(2) is not None:
                if r.group(2).isnumeric():
                    self.page_ranks.append((r.group(1), int(r.group(2))))
                else:
                    print "Non numeric page rank found `" + r.group(2) + "` for url `" + r.group(1) + "`"

    def extract_tags(self):
        pattern = re.compile('(.+?)(?:(?:\[tags:(.+?)])|(?:\[page_rank:(?:.+?)]))+')
        for url in self.start_urls:
            r = pattern.search(url)
            if r is not None:
                if r.group(2) is not None:
                    self.tags.append((r.group(1), r.group(2).split(',')))
                self.start_urls[self.start_urls.index(url)] = r.group(1)

    def parse_item(self, response):
        if "text/html" not in response.headers['Content-Type']:
            return

        self.scrap_content(response)

    def scrap_content(self, response):
        try:
            body = response.body.decode(response.encoding)
        except UnicodeDecodeError:
            body = response.body
            print "decoding failed"

        doc = lxml.html.fromstring(body)

        for selector in self.selectors_exclude:
            exclude_selector = CSSSelector(selector)
            bads = exclude_selector(doc)

            if len(bads) > 0:
                for bad in bads:
                    bad.getparent().remove(bad)

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

            content = self.get_element_content(el)
            if len(content) > 0:
                blocs.append(((el, content), current_selector))

        self.index_document(blocs, response)

    def index_document(self, blocs, response):
        objects = self.stategy.create_objects_from_document(blocs, response, self.tags, self.page_ranks)

        print response.url

        for i in xrange(0, len(objects), 50):
            self.algolia_helper.add_objects(objects[i:i + 50])

    def is_same_element(self, el1, el2):
        return el1.getroottree().getpath(el1) == el2.getroottree().getpath(el2)

    def find_matching_el(self, el, l):
        for elem in l:
            if self.is_same_element(el, elem):
                return True
        return False

    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s += ' ' + x.strip(' \t\n\r')

        return re.sub('\s+', ' ', s.strip(self.strip_chars))
