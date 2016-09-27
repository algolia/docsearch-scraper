import re
from selenium import webdriver

from ..custom_middleware import CustomMiddleware
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
            driver = webdriver.Firefox()
            driver.implicitly_wait(1)
            CustomMiddleware.driver = driver
            JsExecutor.driver = driver

        return driver

    @staticmethod
    def destroy(driver):
        # Start firefox if needed
        if driver is not None:
            driver.quit()
            driver = None

        return driver
