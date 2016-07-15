# coding: utf-8
import pytest

from ...config_loader import ConfigLoader
from .abstract import config


class TestStartUrls:
    def test_mandatory_start_urls(self):
        """ Should throw if no start_urls passed """
        # Given
        config({
            'start_urls': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_start_urls_accept_single_value(self):
        """ Allow passing start_urls as string instead of array """
        # Given
        config({
            'start_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['url'] == 'www.foo.bar'

    def test_start_urls_should_have_at_least_one_element(self):
        """ Should throw if start_urls does not have at least one element """
        # Given
        config({
            'start_urls': []
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_start_url_should_add_default_page_rank_and_tags(self):
        """ Should add default values for page_rank and tags """
        # Given
        config({
            'start_urls': [{"url": "http://www.foo.bar/"}]
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['tags'] == []
        assert actual.start_urls[0]['page_rank'] == 0

    def test_start_url_should_be_transform_to_object_if_string(self):
        """ Should accept strings for start_urls as well as objects """
        # Given
        config({
            'start_urls': ['http://www.foo.bar/']
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['url'] == 'http://www.foo.bar/'

    def test_start_urls_should_be_generated_when_there_is_automatic_tagging(self, monkeypatch):
        from .mocked_init import MockedInit
        monkeypatch.setattr("selenium.webdriver.Firefox", lambda: MockedInit())
        monkeypatch.setattr("time.sleep", lambda x: "")

        # When
        config({
            "start_urls": [
                {
                    "url": "https://test.com/doc/(?P<version>.*?)/(?P<type_of_content>.*?)/",
                    "variables": {
                        "version": ["1.0", "1.1"],
                        "type_of_content": ["book", "bundles", "reference", "components", "cookbook", "best_practices"]
                    }
                }
            ]
        })

        actual = ConfigLoader()

        assert len(actual.start_urls) == 12
        assert actual.start_urls[0]['url'] == "https://test.com/doc/1.0/book/"
