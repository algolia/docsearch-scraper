"""
DocumentationSpider
"""
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time

class DocumentationSpider(CrawlSpider):
    """
    DocumentationSpider
    """
    algolia_helper = None
    strategy = None

    def __init__(self, config, algolia_helper, strategy, *args, **kwargs):

        # Scrapy config
        self.name = config.index_name
        self.allowed_domains = config.allowed_domains
        self.start_urls = [start_url['url'] for start_url in config.start_urls]
        self.stop_urls = config.stop_urls

        self.algolia_helper = algolia_helper
        self.strategy = strategy

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow=self.start_urls,
            deny=self.stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src')
        )
        DocumentationSpider.rules = [
            Rule(link_extractor, callback="callback", follow=True)
        ]
        super(DocumentationSpider, self)._compile_rules()

    def stop_and_close(self):
        raise CloseSpider('CLOSE')

    def callback(self, response):
        """Callback fired on each page scrapped"""
        if "text/html" not in response.headers['Content-Type']:
            return

        print response.url

        records = self.strategy.get_records_from_response(response)
        self.algolia_helper.add_records(records)

