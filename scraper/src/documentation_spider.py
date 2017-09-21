"""
DocumentationSpider
"""
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request

# Import for the sitemap behavior
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import regex, iterloc
import six

# End of import for the sitemap behavior

try:
    from urlparse import urlparse
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus


class DocumentationSpider(CrawlSpider, SitemapSpider):
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
        self.scrap_start_urls = config.scrap_start_urls
        self.remove_get_params = config.remove_get_params

        self.strict_redirect = config.strict_redirect

        super(DocumentationSpider, self).__init__(*args, **kwargs)
        link_extractor = LxmlLinkExtractor(
            allow=self.start_urls,
            deny=self.stop_urls,
            tags=('a', 'area', 'iframe'),
            attrs=('href', 'src'),
            canonicalize=(not config.js_render or not config.use_anchors)
        )

        DocumentationSpider.rules = [
            Rule(link_extractor, callback=self.parse_from_start_url, follow=True),
        ]

        # START _init_ part from SitemapSpider
        # We son't want to check anything if we don't even have a sitemap URL
        if config.sitemap_urls:
            # In case we don't have a special documentation regex, we assume that start_urls are there to match a documentation part
            self.sitemap_urls_regexs = config.sitemap_urls_regexs if config.sitemap_urls_regexs else self.start_urls
            sitemap_rules = []
            for regex in self.sitemap_urls_regexs:
                sitemap_rules.append((regex, 'parse_from_sitemap'))
            self.__init_sitemap_(config.sitemap_urls, sitemap_rules)

            self.force_sitemap_urls_crawling = config.force_sitemap_urls_crawling
        # END _init_ part from SitemapSpider

        super(DocumentationSpider, self)._compile_rules()

    def start_requests(self):

        # We crawl according to the sitemap
        for i in self.start_requests_sitemap():
            yield i

        # We crawl the start point in order to ensure we didn't miss anything
        for url in self.start_urls:
            if self.scrap_start_urls:
                yield Request(url, dont_filter=False, callback=self.parse_from_start_url)
            else:
                yield Request(url, dont_filter=False)

    def add_records(self, response):
        records = self.strategy.get_records_from_response(response)
        self.algolia_helper.add_records(records, response.url)

        DocumentationSpider.NB_INDEXED += len(records)


    # Start request by sitemap
    def start_requests_sitemap(self):
        print "> Browse sitemap"
        for url in self.sitemap_urls:
            yield Request(url, self._parse_sitemap)

    def parse_from_sitemap(self, response):
        if (not self.force_sitemap_urls_crawling) and (not self.is_rules_compliant(response)):
            print("\033[94m> Ignored from sitemap:\033[0m " + response.url)
        else:
            self.add_records(response)

        return self.parse(response)

    def parse_from_start_url(self, response):
        if self.is_rules_compliant(response):
            self.add_records(response)
        else:
            print("\033[94m> Ignored: from start url\033[0m " + response.url)

        return self.parse(response)

    def is_rules_compliant(self, response):
        # Even if the link extract were compliant, we may have been redirected. Hence we check a new time
        if not (response.url.endswith('/sitemap.xml')):
            for rule in self._rules:
                if not self.strict_redirect:
                    if rule.link_extractor._link_allowed(response):
                        continue

                    if rule.link_extractor._link_allowed(response.request):
                        response.replace(url=response.request.url)
                        continue
                else:
                    if rule.link_extractor._link_allowed(response) and rule.link_extractor._link_allowed(response.request):
                        continue

                if response.request.url in self.start_urls and self.scrap_start_urls is False:
                    continue

                if not (self.scrap_start_urls and response.url in self.start_urls):
                    return False
        return True

    # Init method of a SiteMapSpider @Scrapy
    def __init_sitemap_(self, sitemap_urls, custom_sitemap_rules):
        # print "__init_sitemap_"
        self.sitemap_urls = sitemap_urls
        self.sitemap_rules = custom_sitemap_rules
        self._cbs = []
        for r, c in self.sitemap_rules:
            if isinstance(c, six.string_types):
                c = getattr(self, c)
            self._cbs.append((regex(r), c))
        self._follow = [regex(x) for x in self.sitemap_follow]