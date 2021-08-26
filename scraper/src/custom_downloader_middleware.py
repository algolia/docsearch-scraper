"""
CustomDownloaderMiddleware
"""

import time

from scrapy.http import HtmlResponse
from urllib.parse import urlparse, unquote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from uuid import uuid4;
import re

class CustomDownloaderMiddleware:
    driver = None
    auth_cookie = None
    wait_selectors = []

    def __init__(self):
        self.wait_selectors = CustomDownloaderMiddleware.wait_selectors
        self.driver = CustomDownloaderMiddleware.driver
        self.initialized_auth = False

    def process_request(self, request, spider):
        if not spider.js_render:
            return None

        if spider.remove_get_params:
            o = urlparse(request.url)
            url_without_params = o.scheme + "://" + o.netloc + o.path
            request = request.replace(url=url_without_params)

        if self.auth_cookie and not self.initialized_auth:
            self.driver.get(unquote_plus(request.url))
            self.driver.add_cookie(self.auth_cookie)
            self.initialized_auth = True

        print("Getting " + request.url + " from selenium")

        temp_ids = []
        for selector in self.wait_selectors:
            id = uuid4()
            temp_ids.append(id)
            if self.element_exists(selector['selector']):
                self.driver.execute_script('document.evaluate("{}", document.getElementsByTagName("body").item(0)).iterateNext().id = "{}"'.format(selector['selector'], id))

        self.driver.get(unquote_plus(
            request.url))  # Decode url otherwise firefox is not happy. Ex /#%21/ => /#!/%21
        time.sleep(spider.js_wait)

        for selector, id in zip(self.wait_selectors, temp_ids):
            exclude_pages = selector.get('exclude_pages', None)

            if not exclude_pages or not re.search(exclude_pages, self.driver.current_url):
                WebDriverWait(self.driver, 30).until_not(
                    expected_conditions.presence_of_element_located((By.ID, id))
                )
                WebDriverWait(self.driver, 30).until(
                    expected_conditions.presence_of_element_located((By.XPATH, selector['selector']))
                )

        body = self.driver.page_source.encode('utf-8')
        url = self.driver.current_url

        return HtmlResponse(
            url=url,
            body=body,
            encoding='utf8'
        )

    def element_exists(self, xpath):
        return len(self.driver.find_elements_by_xpath(xpath)) > 0

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

        return response
