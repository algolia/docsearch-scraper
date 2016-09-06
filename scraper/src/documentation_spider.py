"""
DocumentationSpider
"""
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from os import environ

class DocumentationSpider(CrawlSpider):
    """
    DocumentationSpider
    """
    algolia_helper = None
    strategy = None
    js_render = False
    js_wait = 0

    def __init__(self, config, algolia_helper, strategy, *args, **kwargs):
        global basic_auth
        basic_auth = 'HTTP_USER' in environ and 'HTTP_PASS' in environ

        # Scrapy config
        self.name = config.index_name

        if basic_auth:
            self.http_user = environ['HTTP_USER']
            self.http_pass = environ['HTTP_PASS']

        self.allowed_domains = config.allowed_domains
        self.start_urls = [start_url['url'] for start_url in config.start_urls]
        self.stop_urls = config.stop_urls

        self.algolia_helper = algolia_helper
        self.strategy = strategy
        self.js_render = config.js_render
        self.js_wait = config.js_wait
        self.scrap_start_urls = config.scrap_start_urls
        self.remove_get_params = config.remove_get_params

        self.strict_redirect = config.strict_redirect

        process_value = self.process_url if basic_auth else null;

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow='.*',
            deny=self.stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src'),
            canonicalize=(not config.js_render or not config.use_anchors),
            process_value=process_value
        )

        DocumentationSpider.rules = [
            Rule(link_extractor, callback=self.add_records, follow=False),
        ]

        super(DocumentationSpider, self)._compile_rules()



    #append basic auth params to end of each url for crawling
    def process_url(self, x):
        if not x.endswith('/'):
            x = x + '/'
        if "?" not in x:
            return x + "?auth=basic"
        else:
            return ''

    def start_requests(self):
        for url in self.start_urls:
            mod_url = url + '?auth=basic' if basic_auth else url
            if self.scrap_start_urls:
                yield Request(mod_url, meta={'dont_redirect': True}, dont_filter=False, callback=self.add_records)
            else:
                yield Request(mod_url, meta={'dont_redirect': True}, dont_filter=False)

    def link_filtering(self, links):
        new_links = []
        for link in links:
            link.url = (link.url[-1] == '/' and link.url[:-1] or link.url)
            new_links.append(link)
        return new_links

    def add_records(self, response):
        records = self.strategy.get_records_from_response(response)
        
        #strip basic auth params before adding to index
        if basic_auth:
            response = response.replace(url=response.url.replace("?auth=basic", ""))
        self.algolia_helper.add_records(records, response.url)

        DocumentationSpider.NB_INDEXED += len(records)

        return self.parse(response)
