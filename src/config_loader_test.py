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

    def test_access_urls(self):
        # Given
        self.config({})

        # When
        actual = ConfigLoader()

        # Then
        assert actual.start_urls == 'start_urls'
        assert actual.allow_urls == 'allow_urls'
        assert actual.deny_urls == 'deny_urls'

