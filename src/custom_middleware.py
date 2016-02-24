"""
CustomMiddleware
"""

from scrapy.http import Request, HtmlResponse
from scrapy.exceptions import IgnoreRequest

import json
import time

class CustomMiddleware(object):
    def __init__(self):
        self.seen = {}
        self.driver = CustomMiddleware.driver

    def process_request(self, request, spider):

        if not spider.js_render:
            return None

        if request.url in self.seen:
            return None

        self.seen[request.url] = True

        print "Getting " + request.url + " from selenium"

        self.driver.get(request.url)
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
        for rule in spider._rules:
            if not rule.link_extractor._link_allowed(response) and not (spider.scrap_start_urls and response.url in spider.start_urls):
                print "Ignored: " + response.url
                raise IgnoreRequest()

        return response

