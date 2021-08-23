"""
CustomDownloaderMiddleware
"""

import time

from scrapy.http import HtmlResponse
from urllib.parse import urlparse, unquote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

HEADER_SPAN_XPATH = "//section/article/{}//span"
ARTICLE_CONTENT_SELECTOR = '//section/article[./h1 or ./h2]'
SIDEBAR_CONTENT_SELECTOR = "//aside//li[@class='active']"
TEMP_CONTENT_ID = "temp-docsearch-scraper-content-id"
TEMP_SIDEBAR_ID = "temp-docsearch-scraper-sidebar-id"

class CustomDownloaderMiddleware:
    driver = None
    auth_cookie = None

    def __init__(self):
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

        h1_xpath = HEADER_SPAN_XPATH.format('h1')
        h2_xpath = HEADER_SPAN_XPATH.format('h2')
        if self.element_exists(h1_xpath):
            self.driver.execute_script('document.evaluate("{}", document.getElementsByTagName("body").item(0)).iterateNext().id = "{}"'.format(h1_xpath, TEMP_CONTENT_ID))
        elif self.element_exists(h2_xpath):
            self.driver.execute_script('document.evaluate("{}", document.getElementsByTagName("body").item(0)).iterateNext().id = "{}"'.format(h2_xpath, TEMP_CONTENT_ID))

        if self.element_exists(SIDEBAR_CONTENT_SELECTOR):
            self.driver.execute_script('document.evaluate("{}", document.getElementsByTagName("body").item(0)).iterateNext().id = "{}"'.format(SIDEBAR_CONTENT_SELECTOR, TEMP_SIDEBAR_ID))

        self.driver.get(unquote_plus(
            request.url))  # Decode url otherwise firefox is not happy. Ex /#%21/ => /#!/%21
        time.sleep(spider.js_wait)

        # Wait until old content has disappeared and new one is visible
        WebDriverWait(self.driver, 30).until_not(
            expected_conditions.presence_of_element_located((By.ID, TEMP_CONTENT_ID))
        )
        WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located((By.XPATH, ARTICLE_CONTENT_SELECTOR))
        )

        # Wait until old sidebar has unloaded and new one is visible
        # If we are on the home page then we'll have many more chances to grab links from the sidebar,
        # so it's okay if the sidebar isn't loaded.
        hash = urlparse(request.url).fragment
        if len(hash) > 0 and hash != '/':
            WebDriverWait(self.driver, 30).until_not(
                expected_conditions.presence_of_element_located((By.ID, TEMP_SIDEBAR_ID))
            )
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located((By.XPATH, SIDEBAR_CONTENT_SELECTOR))
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
