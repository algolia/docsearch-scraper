# coding: utf-8
"""ConfigLoader tests"""
from config_loader import ConfigLoader
import pytest
import os
import json


class TestInit:
    def config(self, additional_config={}):
        base_config = {
            'allowed_domains': 'allowed_domains',
            'api_key': 'api_key',
            'app_id': 'app_id',
            'custom_settings': 'custom_settings',
            'hash_strategy': 'hash_strategy',
            'index_name': 'index_name',
            'index_prefix': 'index_prefix',
            'selectors': 'selectors',
            'selectors_exclude': 'selectors_exclude',
            'start_urls': 'start_urls',
            'stop_urls': 'http://www.stopurl.com/',
            'strategy': 'strategy',
            'strip_chars': 'strip_chars'
        }
        config = base_config.copy()
        config.update(additional_config)
        os.environ['CONFIG'] = json.dumps(config)


    @staticmethod
    def test_need_config_environment_variable():
        """ Should throw if no CONFIG passed"""
        # Given
        os.environ['CONFIG'] = ''

        # When / Then
        with pytest.raises(SystemExit):
            ConfigLoader()

    @staticmethod
    def test_need_json_env_var():
        """ Should throw if CONFIG is not JSON """
        # Given
        os.environ['CONFIG'] = 'foobar'

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_mandatory_index_name(self):
        """ Should throw if no index_name passed """
        # Given
        self.config({
            'index_name': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_allowed_domains_accept_single_value(self):
        """ Should allow passing allowed_domains as a string instead of an array
        """
        # Given
        self.config({
            'allowed_domains': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar']

    def test_mandatory_start_urls(self):
        """ Should throw if no start_urls passed """
        # Given
        self.config({
            'start_urls': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_start_urls_accept_single_value(self):
        """ Allow passing start_urls as string instead of array """
        # Given
        self.config({
            'start_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['url'] == 'www.foo.bar'

    def test_stop_urls_accept_single_value(self):
        """ Allow passing stop_urls as string instead of array """
        # Given
        self.config({
            'stop_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.stop_urls == ['www.foo.bar']


    def test_start_urls_should_have_at_least_one_element(self):
        """ Should throw if start_urls does not have at least one element """
        # Given
        self.config({
            'start_urls': []
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_allowed_domains_start(self):
        """ Should populate allowed_domains from start_urls """
        # Given
        self.config({
            'start_urls': 'http://www.foo.bar/',
            'stop_urls': [],
            'allowed_domains': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar']
    
    def test_allowed_domains_start_stop(self):
        """ Should populate allowed_domains from both start and stop urls """
        # Given
        self.config({
            'start_urls': 'http://www.foo.bar/',
            'stop_urls': 'http://www.algolia.com/',
            'allowed_domains': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar', 'www.algolia.com']

    def test_allowed_domains_unique(self):
        """ Should populate a list of unique domains """
        # Given
        self.config({
            'start_urls': 'http://www.foo.bar/',
            'stop_urls': [
                'http://www.algolia.com/',
                'http://www.foo.bar/'
            ],
            'allowed_domains': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar', 'www.algolia.com']

    def test_start_url_should_add_default_page_rank_and_tags(self):
        # Given
        self.config({
            'start_urls': [{"url": "http://www.foo.bar/"}]
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['tags'] == []
        assert actual.start_urls[0]['page_rank'] == 0

    def test_start_url_should_be_transform_to_object_if_string(self):
        # Given
        self.config({
            'start_urls': ['http://www.foo.bar/']
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls[0]['url'] == 'http://www.foo.bar/'

    def test_default_strategy(self):
        """ Should use default strategy if none is passed """
        # When
        self.config({
            'strategy': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.strategy == 'default'

