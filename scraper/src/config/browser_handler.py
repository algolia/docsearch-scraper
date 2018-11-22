import re
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from ..custom_downloader_middleware import CustomDownloaderMiddleware
from ..js_executor import JsExecutor


class BrowserHandler:
    @staticmethod
    def conf_need_browser(config_original_content, js_render):
        group_regex = re.compile("\\(\?P<(.+?)>.+?\\)")
        results = re.findall(group_regex, config_original_content)

        return len(results) > 0 or js_render

    @staticmethod
    def init(config_original_content, js_render):
        driver = None

        if BrowserHandler.conf_need_browser(config_original_content,
                                            js_render):
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')

            CustomDownloaderMiddleware.driver = driver
            JsExecutor.driver = driver

            driver = webdriver.Chrome("/usr/bin/chromedriver",
                                      chrome_options=chrome_options)
        return driver

    @staticmethod
    def destroy(driver):
        # Start firefox if needed
        if driver is not None:
            driver.quit()
            driver = None

        return driver
