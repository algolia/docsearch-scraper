# coding: utf-8

from src.config_loader import ConfigLoader
from abstract import config

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