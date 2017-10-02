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
import re

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
    match_capture_any_scheme = r"^(https?)(.*)"
    backreference_any_scheme = r"^https?\2(.*)$"
    every_schemes = ["http", "https"]

    @staticmethod
    def to_any_scheme(url):
        """Return an regex that represent the URL and is scheme agnostic """
        return url if not re.match(DocumentationSpider.match_capture_any_scheme, url) else re.sub(
            DocumentationSpider.match_capture_any_scheme, DocumentationSpider.backreference_any_scheme, url)

    @staticmethod
    def to_each_scheme(url):
        """Return a list with the translation to this url into each scheme. The first one will be the original one if it has a scheme"""
        url_with_each_scheme = []
        url = url.encode('utf8')
        for scheme in DocumentationSpider.every_schemes:
            url_with_scheme = re.sub(DocumentationSpider.match_capture_any_scheme, scheme + "\\2", url)
            if re.match("^" + scheme + '.*', url):
                url_with_each_scheme = [url_with_scheme] + url_with_each_scheme
            else:
                url_with_each_scheme = url_with_each_scheme + [url_with_scheme]
        return url_with_each_scheme

    @staticmethod
    def list_to_each_scheme(urls):
        """ Return a flatten list containing each URL into each different schemes. Considering the different URL related to the same one, the first one will be the one with the scheme given as input"""
        # Performance purpose https://stackoverflow.com/questions/406121/flattening-a-shallow-list-in-python
        return [scheme_url for url in urls for scheme_url in DocumentationSpider.to_each_scheme(url)]

    def __init__(self, config, algolia_helper, strategy, *args, **kwargs):

        # Scrapy config
        self.name = config.index_name
        self.allowed_domains = config.allowed_domains
        self.start_urls = [start_url['url'] for start_url in config.start_urls]
        # TODO make stop_urls scheme agnostic => enhance to_any_scheme => remove deny_no_scheme (try position when no match)
        # We need to ensure that the stop urls are scheme agnostic if it represents URL
        self.stop_urls = map(DocumentationSpider.to_any_scheme, config.stop_urls)
        self.algolia_helper = algolia_helper
        self.strategy = strategy
        self.js_render = config.js_render
        self.js_wait = config.js_wait
        self.scrape_start_urls = config.scrape_start_urls
        self.remove_get_params = config.remove_get_params

        self.strict_redirect = config.strict_redirect

        super(DocumentationSpider, self).__init__(*args, **kwargs)

        # Get rid of scheme consideration http is equivalent to https
        # Start_urls must stays authentic URL in order to be reached, we build agnostic scheme regex based on those URL
        self.start_urls_any_scheme = map(DocumentationSpider.to_any_scheme, self.start_urls)
        start_urls_any_scheme = map(DocumentationSpider.to_any_scheme, self.start_urls)
        print "start_urls_any_scheme"
        print start_urls_any_scheme
        link_extractor = LxmlLinkExtractor(
            allow=start_urls_any_scheme,
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
            self.sitemap_urls_regexs = config.sitemap_urls_regexs if config.sitemap_urls_regexs else start_urls_any_scheme
            sitemap_rules = []
            if self.sitemap_urls_regexs:
                for regex in self.sitemap_urls_regexs:
                    sitemap_rules.append((regex, 'parse_from_sitemap'))
            else:  # None start url nor regex: default, we parse all
                print "None start url nor regex: default, we scrap all"
                sitemap_rules = [('.*', 'parse_from_sitemap')]

            self.__init_sitemap_(config.sitemap_urls, sitemap_rules)
            self.force_sitemap_urls_crawling = config.force_sitemap_urls_crawling
        # END _init_ part from SitemapSpider

        super(DocumentationSpider, self)._compile_rules()

    def start_requests(self):

        # We crawl according to the sitemap
        if self.sitemap_urls:
            for request in self.start_requests_sitemap():
                yield request

        # We crawl the start URL in order to ensure we didn't miss anything (Even if we used the sitemap)
        for position, url in enumerate(DocumentationSpider.list_to_each_scheme(self.start_urls)):
            if position % len(DocumentationSpider.every_schemes) == 0:
                # Original URL from the configuration
                if self.scrape_start_urls:
                    yield Request(url, dont_filter=False, callback=self.parse_from_start_url)
                else:
                    yield Request(url, dont_filter=False)
            else:
                # In case the provided scheme isn't available, we try it with the other scheme (Bad config provided)
                # The dupefilter must not filter it since each scheme URL from one url have the same fingerprint (fingerprint  are scheme agnostic)
                yield Request(url, dont_filter=True)

    def add_records(self, response, from_sitemap):
        records = self.strategy.get_records_from_response(response)
        self.algolia_helper.add_records(records, response.url, from_sitemap)

        DocumentationSpider.NB_INDEXED += len(records)

    # Start request by sitemap
    def start_requests_sitemap(self):
        print "> Browse sitemap"
        for position, url in enumerate(DocumentationSpider.list_to_each_scheme(self.sitemap_urls)):
            if position % len(DocumentationSpider.every_schemes) == 0:
                # Original url from the configuration
                yield Request(url, self._parse_sitemap)
            else:
                # In case the provided scheme isn't available, we try it with the other scheme (Bad config provided)
                yield Request(url, self._parse_sitemap, dont_filter=True)

    def parse_from_sitemap(self, response):
        if (not self.force_sitemap_urls_crawling) and (not self.is_rules_compliant(response)):
            print("\033[94m> Ignored from sitemap:\033[0m " + response.url)
        else:
            self.add_records(response, from_sitemap=True)
            # We don't return self.parse(response) in order to avoid crawling those web page

    def parse_from_start_url(self, response):
        if self.is_rules_compliant(response):
            self.add_records(response, from_sitemap=False)
        else:
            print("\033[94m> Ignored: from start url\033[0m " + response.url)

        return self.parse(response)

    def is_rules_compliant(self, response):

        # Even if the link extract were compliant, we may have been redirected. Hence we check a new time

        # Redirection redirect on a start url
        if not self.scrape_start_urls and (response.url in self.start_urls or response.request.url in self.start_urls):
            return False

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
