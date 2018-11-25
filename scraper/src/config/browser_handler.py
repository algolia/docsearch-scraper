import re
import os
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
            chrome_options.add_argument('--allow-insecure-localhost')

            CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH',
                                               "/usr/bin/chromedriver")
            if not os.path.isfile(CHROMEDRIVER_PATH):
                raise Exception(
                    "Env CHROMEDRIVER_PATH='{}' is not a path to a file".format(
                        CHROMEDRIVER_PATH))
            driver = webdriver.Chrome(
                CHROMEDRIVER_PATH,
                chrome_options=chrome_options)
            CustomDownloaderMiddleware.driver = driver
            JsExecutor.driver = driver
        return driver

    @staticmethod
    def destroy(driver):
        # Start firefox if needed
        if driver is not None:
            driver.quit()
            driver = None

        return driver
