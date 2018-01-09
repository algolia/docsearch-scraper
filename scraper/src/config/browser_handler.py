import re
from selenium import webdriver

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

        if BrowserHandler.conf_need_browser(config_original_content, js_render):
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.http.accept-encoding.secure', 'gzip, deflate')
            profile.set_preference('network.http.spdy.enabled.http2', False)
            profile.set_preference('permissions.default.image', 2)
            driver = webdriver.Firefox(profile)
            driver.implicitly_wait(1)
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
