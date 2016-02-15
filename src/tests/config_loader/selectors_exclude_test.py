# coding: utf-8

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
