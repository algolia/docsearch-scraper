# coding: utf-8
"""
Load the config json file.
"""

from collections import OrderedDict
import json
import os
import re
import copy

from selenium import webdriver

from ..custom_middleware import CustomMiddleware
from ..js_executor import JsExecutor
from .config_validator import ConfigValidator
from .nb_hits_updater import NbHitsUpdater
from .urls_parser import UrlsParser
from .selectors_parser import SelectorsParser

try:
    from urlparse import urlparse
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus


class ConfigLoader(object):
    """
    ConfigLoader
    """
    # We define them here so the linters/autocomplete know what to expect
    allowed_domains = None
    api_key = None
    app_id = None
    custom_settings = None
    extra_records = []
    index_name = None
    js_wait = 0
    js_render = False
    keep_tags = []
    min_indexed_level = 0
    remove_get_params = False
    scrap_start_urls = True
    selectors = None
    selectors_exclude = []
    start_urls = None
    stop_urls = []
    stop_content = []
    strategy = 'default'
    strict_redirect = False
    strip_chars = u".,;:§¶"
    use_anchors = False

    # data storage, starting here attribute are not config params
    config_file = None
    config_content = None
    config_original_content = None

    driver = None

    def __init__(self, config):
        if os.path.isfile(config):
            self.config_file = config
            with open(self.config_file, 'r') as f:
                config = f.read()

        try:
            self.config_original_content = config
            data = json.loads(config, object_pairs_hook=OrderedDict)
            self.config_content = copy.deepcopy(data)
        except ValueError:
            raise ValueError('CONFIG is not a valid JSON')

        # Fill self from config
        for key, value in data.items():
            setattr(self, key, value)

        # Start browser if needed
        if self.conf_need_browser():
            self.init()

        # Validate
        ConfigValidator(self).validate()

        # Modify
        self._parse()
        self._parse_env()

        # Stop browser if needed
        if self.conf_need_browser() and not self.js_render:
            self.destroy()

    def _parse_env(self):
        self.app_id = os.environ['APPLICATION_ID']
        self.api_key = os.environ['API_KEY']

    def _parse(self):
        self.selectors = SelectorsParser().parse(self.selectors)
        self.min_indexed_level = SelectorsParser().parse_min_indexed_level(self.min_indexed_level)
        self.start_urls = UrlsParser().parse(self.start_urls)

        # Build default allowed_domains from start_urls and stop_urls
        if self.allowed_domains is None:
            self.allowed_domains = UrlsParser().build_allowed_domains(self.start_urls, self.stop_urls)

    def conf_need_browser(self):
        group_regex = re.compile("\\(\?P<(.+?)>.+?\\)")
        results = re.findall(group_regex, self.config_original_content)

        return len(results) > 0 or self.js_render

    def init(self):
        # Start firefox if needed
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(1)
        CustomMiddleware.driver = self.driver
        JsExecutor.driver = self.driver

    def destroy(self):
        # Start firefox if needed
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def update_nb_hits(self, nb_hits):
        if self._is_loaded_from_file():
            nb_hit_updater = NbHitsUpdater(self.config_file, self.config_content, self._get_config_file_nb_hit(), nb_hits)
            nb_hit_updater.update()

    def get_extra_facets(self):
        extra_facets = []
        for start_url in self.start_urls:
            for tag in start_url['url_attributes']:
                extra_facets.append(tag)

        extra_facets = set(extra_facets)

        return list(extra_facets)

    def get_extra_records(self):
        return self.extra_records

    def _get_config_file_nb_hit(self):
        return None if 'nb_hits' not in self.config_content else self.config_content['nb_hits']

    def _is_loaded_from_file(self):
        return self.config_file is not None
