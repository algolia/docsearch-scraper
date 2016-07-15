# coding: utf-8
from ...config_loader import ConfigLoader
from .abstract import config

class TestDefaultStategy:
    def test_default_strategy(self):
        """ Should use default strategy if none is passed """
        # When
        config({
            'strategy': None
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.strategy == 'default'
