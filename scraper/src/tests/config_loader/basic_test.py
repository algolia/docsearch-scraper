# coding: utf-8

from __future__ import absolute_import
import os

from src.config_loader import ConfigLoader
from .abstract import config
import pytest


class TestInit:
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
        config({
            'index_name': None
        })

        # When / Then
        with pytest.raises(ValueError):
            ConfigLoader()

