"""
PhantomMiddleware
"""

from scrapy.http import Request, HtmlResponse

import json

class PhantomMiddleware(object):
    phantom_url = 'http://localhost:8090'
    seen = []

    def process_request(self, request, spider):
        # If the JS rendering is not needed
        if not spider.js_render:
            return None

        # Skip already processed requests
        if request.url == self.phantom_url:
            return None

        # Avoid to crawl the same page multiple times
        if request.url in self.seen:
            return None
        self.seen.append(request.url)

        body = json.dumps({'url': request.url, 'js_wait': spider.js_wait})
        request = Request(
                url=self.phantom_url,
                meta={'download_timeout': spider.download_timeout},
                method='POST',
                callback=spider.add_records,
                body=body,
        )
        return request

    def process_response(self, request, response, spider):
        if 'original_url' in response.headers:
            original_url = response.headers['original_url']
            response = HtmlResponse(url=original_url, body=response.body, headers=response.headers)

        return response

