# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import os

from src.config_loader import ConfigLoader
from src.strategies.default_strategy import DefaultStrategy

SELECTORS = {
    "lvl0": "h1",
    "lvl1": "h2",
    "lvl2": "h3",
    "lvl3": "h4",
    "lvl4": "h5",
    "lvl5": "h6",
    "content": "p"
}


def get_strategy(config=None):

    if config is None:
        config = {}

    global SELECTORS

    modified_config = {
        'allowed_domains': 'test',
        'api_key': 'test',
        'app_id': 'test',
        'custom_settings': None,
        'hash_strategy': 'test',
        'index_name': 'test',
        'index_prefix': 'test',
        'selectors': SELECTORS,
        'selectors_exclude': 'test',
        'start_urls': 'test',
        'stop_urls': 'test',
        'strategy': 'test'
    }

    for key in config:
        modified_config[key] = config[key]

    # Stub ENV variables read by ConfigLoader
    os.environ['CONFIG'] = json.dumps(modified_config)
    return DefaultStrategy(ConfigLoader())
