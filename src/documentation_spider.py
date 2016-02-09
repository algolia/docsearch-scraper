"""
DocumentationSpider
"""
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

class DocumentationSpider(CrawlSpider):
    """
    DocumentationSpider
    """
    algolia_helper = None
    strategy = None
    js_render = False
    js_wait = 0

    def __init__(self, config, algolia_helper, strategy, *args, **kwargs):

        # Scrapy config
        self.name = config.index_name
        self.allowed_domains = config.allowed_domains
        self.start_urls = [start_url['url'] for start_url in config.start_urls]
        self.stop_urls = config.stop_urls

        self.algolia_helper = algolia_helper
        self.strategy = strategy
        self.js_render = config.js_render
        self.js_wait = config.js_wait

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow=self.start_urls,
            deny=self.stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src'),
            canonicalize=(not config.use_anchors)
        )

        DocumentationSpider.rules = [
            Rule(link_extractor, callback=self.add_records, follow=True),
        ]

        super(DocumentationSpider, self)._compile_rules()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, callback=self.add_records)

    def link_filtering(self, links):
        new_links = []
        for link in links:
            link.url = (link.url[-1] == '/' and link.url[:-1] or link.url)
            new_links.append(link)
        return new_links

    def add_records(self, response):
        records = self.strategy.get_records_from_response(response)
        self.algolia_helper.add_records(records, response.url)
        return self.parse(response)
