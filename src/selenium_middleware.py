"""
SeleniumMiddleware
"""

from scrapy.http import Request, HtmlResponse

import json
import time

class SeleniumMiddleware(object):
    def __init__(self):
        self.seen = {}
        self.driver = SeleniumMiddleware.driver

    def process_request(self, request, spider):
        # If the JS rendering is not needed
        if not spider.js_render:
            return None

        if request.url in self.seen:
            return None

        self.seen[request.url] = True

        print "Getting " + request.url + " from selenium"

        self.driver.get(request.url)
        time.sleep(spider.js_wait)

        return HtmlResponse(
            url=request.url,
            body=self.driver.page_source.encode('utf-8'),
            encoding='utf8'
        )

    def process_response(self, request, response, spider):
        return response

