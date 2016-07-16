# coding: utf-8
import os

from ...config_loader import ConfigLoader
from .abstract import config
import pytest


class TestInit:
    @staticmethod
    def test_need_json_env_var():
        """ Should throw if CONFIG is not JSON """
        # Given
        c = 'foobar'

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader(c)

    def test_mandatory_index_name(self):
        """ Should throw if no index_name passed """
        # Given
        c = config({
            'index_name': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader(c)
