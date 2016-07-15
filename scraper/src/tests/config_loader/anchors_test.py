# coding: utf-8

from ...config_loader import ConfigLoader
from .abstract import config


class TestAnchors:
    def test_use_anchor_default(self):
        """ Should set the `use_anchors` parameter to True by default """
        # When
        config()
        actual = ConfigLoader()

        # Then
        assert actual.use_anchors is False

    def test_use_anchor_set_to_true(self):
        """ Should set the `use_anchors` parameter to False """
        # When
        config({
            'use_anchors': True
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.use_anchors is True

    def test_use_anchor_set_to_false(self):
        """ Should set the `use_anchors` parameter to False """
        # When
        config({
            'use_anchors': False
        })

        # When
        actual = ConfigLoader()

        # Then
        assert actual.use_anchors is False
