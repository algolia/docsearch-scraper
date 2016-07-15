# coding: utf-8
import json
import os

from ...config_loader import ConfigLoader
from .abstract import config


class TestStopUrls:
    def test_stop_urls_accept_single_value(self):
        """ Allow passing stop_urls as string instead of array """
        # Given
        config({
            'stop_urls': 'www.foo.bar'
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.stop_urls == ['www.foo.bar']

    def test_stop_urls_is_not_mandatory(self):
        """ Allow not passing stop_urls """
        # Given
        conf = {
            'allowed_domains': 'allowed_domains',
            'api_key': 'api_key',
            'app_id': 'app_id',
            'index_name': 'index_name',
            'index_prefix': 'index_prefix',
            'selectors': [],
            'selectors_exclude': [],
            'start_urls': ['http://www.starturl.com/']
        }

        os.environ['CONFIG'] = json.dumps(conf)

        # When
        actual = ConfigLoader()

        # Then
        assert actual.stop_urls == []
