# coding: utf-8

from __future__ import absolute_import

from src.config_loader import ConfigLoader
from .abstract import config

class TestOpenSeleniumBrowser:
    def test_browser_not_needed_by_default(self):
        config()

        actual = ConfigLoader()

        assert actual.conf_need_browser() is False

    def test_browser_needed_when_js_render_true(self, monkeypatch):
        from .mocked_init import MockedInit
        monkeypatch.setattr("selenium.webdriver.Firefox", lambda: MockedInit())
        monkeypatch.setattr("time.sleep", lambda x: "")
        # When
        config({
            "js_render": True
        })

        actual = ConfigLoader()

        assert actual.conf_need_browser() is True

    def test_browser_needed_when_config_contains_automatic_tag(self, monkeypatch):
        from .mocked_init import MockedInit
        monkeypatch.setattr("selenium.webdriver.Firefox", lambda: MockedInit())
        monkeypatch.setattr("time.sleep", lambda x: "")

        # When
        config({
            "start_urls": [
                {
                    "url": "https://symfony.com/doc/(?P<version>.*?)/(?P<type_of_content>.*?)/",
                    "variables": {
                        "version": {
                            "url": "https://symfony.com/doc/current/book/controller.html",
                            "js":"var versions = $('.doc-switcher .versions li').map(function (i, elt) { return $(elt).find('a').html().split('/')[0].replace(/ |\\n/g,''); }).toArray(); versions.push('current'); return JSON.stringify(versions);"
                        },
                        "type_of_content": ["book", "bundles", "reference", "components", "cookbook", "best_practices"]
                    }
                }
            ]
        })

        actual = ConfigLoader()

        assert actual.conf_need_browser() is True
