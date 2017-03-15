"""
CustomMiddleware
"""

import time

from scrapy.http import Request, HtmlResponse
from scrapy.exceptions import IgnoreRequest

try:
    from urlparse import urlparse
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus

class CustomMiddleware(object):
    def __init__(self):
        self.seen = {}
        self.driver = CustomMiddleware.driver

    def process_request(self, request, spider):

        if not spider.js_render:
            return None

        if spider.remove_get_params:
            o = urlparse(request.url)
            url_without_params = o.scheme + "://" + o.netloc + o.path
            request = request.replace(url=url_without_params)

        if request.url in self.seen:
            return None

        self.seen[request.url] = True

        print("Getting " + request.url + " from selenium")

        self.driver.get(unquote_plus(request.url)) # Decode url otherwise firefox is not happy. Ex /#%21/ => /#!/%21
        time.sleep(spider.js_wait)
        body = self.driver.page_source.encode('utf-8')
        url = self.driver.current_url

        return HtmlResponse(
            url=url,
            body=body,
            encoding='utf8'
        )

    def process_response(self, request, response, spider):
        # Since scrappy use start_urls and stop_urls before creating the request
        # If the url get redirected then this url gets crawled even if it's not allowed to
        # So we check if the final url is allowed

        if spider.remove_get_params:
            o = urlparse(response.url)
            url_without_params = o.scheme + "://" + o.netloc + o.path
            response = response.replace(url=url_without_params)

        if response.url == request.url + '#':
            response = response.replace(url=request.url)

        for rule in spider._rules:
            if not spider.strict_redirect:
                if rule.link_extractor._link_allowed(response):
                    continue

                if rule.link_extractor._link_allowed(request):
                    response.replace(url=request.url)
                    continue
            else:
                if rule.link_extractor._link_allowed(response) and rule.link_extractor._link_allowed(request):
                    continue

            if request.url in spider.start_urls and spider.scrap_start_urls is False:
                continue

            if not (spider.scrap_start_urls and response.url in spider.start_urls):
                print("\033[94m> Ignored:\033[0m " + response.url)
                raise IgnoreRequest()

        return response
