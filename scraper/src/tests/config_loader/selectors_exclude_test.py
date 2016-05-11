# coding: utf-8

import os
import json

from src.config_loader import ConfigLoader
from abstract import config


class TestSelectorsExclude:
    def test_selectors_exclude_default(self):
        """ Should set the `selectors_exclude` parameter to [] by default """

        config()

        # When
        actual = ConfigLoader()

        # Then
        assert actual.selectors_exclude == []

    def test_selectors_exclude_set_override_default(self):
        """ Default `selectors_exclude` should be override when set in the config """
        # When
        config({
            'selectors_exclude': ['.test']
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.selectors_exclude == ['.test']

    def test_selectors_exclude_is_not_mandatory(self):
        """ Allow not passing selectors_exclude """
        # Given
        conf = {
            'allowed_domains': 'allowed_domains',
            'api_key': 'api_key',
            'app_id': 'app_id',
            'index_name': 'index_name',
            'index_prefix': 'index_prefix',
            'selectors': [],
            'start_urls': ['http://www.starturl.com/'],
            'stop_urls': ['http://www.stopurl.com/']
        }

        os.environ['CONFIG'] = json.dumps(conf)

        # When
        actual = ConfigLoader()

        # Then
        assert actual.selectors_exclude == []

