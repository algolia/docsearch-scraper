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
            'allow_urls': 'allow_urls',
            'deny_urls': 'deny_urls',
            'stop_urls': 'stop_urls',
            'strategy': 'strategy',
            'strip_chars': 'strip_chars'
        }
        config = base_config.copy()
        config.update(additional_config)
        os.environ['CONFIG'] = json.dumps(config)
    

    def test_need_config_environment_variable(self):
        # Given
        os.environ['CONFIG'] = ''
        
        # When / Then
        with pytest.raises(SystemExit):
            ConfigLoader()
    
    def test_need_json_env_var(self):
        # Given
        os.environ['CONFIG'] = 'foobar'
        
        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_mandatory_index_name(self):
        # Given
        self.config({
            'index_name': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_allowed_domains_accept_single_value(self):
        # Given
        self.config({
            'allowed_domains': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar']

    def test_mandatory_start_urls(self):
        # Given
        self.config({
            'start_urls': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_accept_stop_urls_as_deny_urls(self):
        # Given
        self.config({
            'stop_urls': ['foo'],
            'deny_urls': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.deny_urls == ['foo']

    def test_start_urls_accept_single_value(self):
        # Given
        self.config({
            'start_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls == ['www.foo.bar']

    def test_deny_urls_accept_single_value(self):
        # Given
        self.config({
            'deny_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.deny_urls == ['www.foo.bar']


    def test_allow_urls_accept_single_value(self):
        # Given
        self.config({
            'allow_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allow_urls == ['www.foo.bar']

    def test_start_urls_should_have_at_least_one_element(self):
        # Given
        self.config({
            'start_urls': []
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

    def test_allowed_domains_uses_start_url_as_default(self):
        # Given
        self.config({
            'start_urls': 'http://www.foo.bar/',
            'allowed_domains': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.allowed_domains == ['www.foo.bar']
