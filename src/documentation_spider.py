"""
DocumentationSpider
"""
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request

class DocumentationSpider(CrawlSpider):
    """
    DocumentationSpider
    """
    algolia_helper = None
    strategy = None
    js_render = False

    def __init__(self, config, algolia_helper, strategy, *args, **kwargs):

        # Scrapy config
        self.name = config.index_name
        self.allowed_domains = config.allowed_domains
        self.start_urls = [start_url['url'] for start_url in config.start_urls]
        self.stop_urls = config.stop_urls

        self.algolia_helper = algolia_helper
        self.strategy = strategy
        self.js_render = config.js_render

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow=self.start_urls,
            deny=self.stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src')
        )

        if self.js_render:
            self.start_requests = self.splash_start_requests
            DocumentationSpider.rules = [
                Rule(link_extractor, callback="callback", process_request="splash_request", follow=True)
            ]
        else:
            DocumentationSpider.rules = [
                Rule(link_extractor, callback="callback", follow=True)
            ]

        super(DocumentationSpider, self)._compile_rules()

    def splash_start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.splash_parse_start_url, meta = {
                'splash': {
                    'endpoint': 'render.html',
                    'args': {'wait': 0.5}
                }
            })

    def splash_parse_start_url(self, response):
        original_url = response.meta['_splash_processed']['args']['url']
        response = response.replace(url=original_url)
        return self.parse(response)

    def splash_request(self, request):
        request.meta['splash'] = {
            'endpoint': 'render.html',
            'args': {'wait': 0.5},
        }
        return request

    def _response_downloaded(self, response):
        if '_splash_processed' in response.meta:
            original_url = response.meta['_splash_processed']['args']['url']
            response = response.replace(url=original_url)

        rule = self._rules[response.meta['rule']]
        return self._parse_response(response, rule.callback, rule.cb_kwargs, rule.follow)

    def stop_and_close(self):
        raise CloseSpider('CLOSE')

    def callback(self, response):
        """Callback fired on each page scrapped"""
        if "text/html" not in response.headers['Content-Type']:
            return

        if self.js_render:
            print response.meta['_splash_processed']['args']['url']
        else:
            print response.url

        records = self.strategy.get_records_from_response(response)
        self.algolia_helper.add_records(records)
