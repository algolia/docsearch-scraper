# coding: utf-8

import os
import json


def config(additional_config={}):
    base_config = {
        'allowed_domains': 'allowed_domains',
        'api_key': 'api_key',
        'app_id': 'app_id',
        'custom_settings': 'custom_settings',
        'hash_strategy': 'hash_strategy',
        'index_name': 'index_name',
        'index_prefix': 'index_prefix',
        'selectors': [],
        'selectors_exclude': [],
        'start_urls': ['http://www.starturl.com/'],
        'stop_urls': ['http://www.stopurl.com/'],
        'strategy': 'strategy',
        'strip_chars': 'strip_chars'
    }
    final_config = base_config.copy()
    final_config.update(additional_config)
    os.environ['CONFIG'] = json.dumps(final_config)
