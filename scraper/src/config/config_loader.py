# coding: utf-8
"""
Load the config json file.
"""

from collections import OrderedDict
import json
import os
import copy
import pprint
from cerberus import Validator


from .config_schema import CONFIG_SCHEMA
from .nb_hits_updater import NbHitsUpdater
from .urls_parser import UrlsParser
from .selectors_parser import SelectorsParser
from .browser_handler import BrowserHandler

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
    scrape_start_urls = True
    selectors = None
    selectors_exclude = []
    start_urls = []
    stop_urls = []
    stop_content = []
    strategy = 'default'
    strict_redirect = True
    strip_chars = u".,;:§¶"
    use_anchors = False
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    only_content_level = False
    query_rules = []

    # data storage, starting here attribute are not config params
    config_file = None
    config_content = None
    config_original_content = None

    driver = None

    sitemap_urls = []
    sitemap_urls_regexs = []
    force_sitemap_urls_crawling = False

    nb_hits_max = 6000000

    def __init__(self, config):
        data = self._load_config(config)

        # Validate
        self._validate_config(data)

        # Fill self from config
        for key, value in data.items():
            setattr(self, key, value)

        # Start browser if needed
        self.driver = BrowserHandler.init(self.config_original_content, self.js_render)

        # Modify
        self._parse()

        # Stop browser if needed
        if not self.js_render:
            self.driver = BrowserHandler.destroy(self.driver)

        # BC new correct naming
        self.scrape_start_urls = self.scrap_start_urls if not self.scrap_start_urls else self.scrape_start_urls

    @staticmethod
    def _validate_config(data):
        config_validator = Validator(CONFIG_SCHEMA)
        is_config_valid = config_validator.validate(data)

        if not is_config_valid:
            raise ValueError(pprint.pformat(config_validator.errors))

    def _load_config(self, config):
        if os.path.isfile(config):
            self.config_file = config
            with open(self.config_file, 'r') as f:
                config = f.read()

        try:
            self.config_original_content = config
            data = json.loads(config, object_pairs_hook=OrderedDict)
            self.config_content = copy.deepcopy(data)

            return data
        except ValueError:
            raise ValueError('CONFIG is not a valid JSON')

    def _parse(self):
        # Parse Env
        self.app_id = os.environ['APPLICATION_ID']
        self.api_key = os.environ['API_KEY']

        # Parse config
        self.selectors = SelectorsParser().parse(self.selectors)
        self.min_indexed_level = SelectorsParser().parse_min_indexed_level(self.min_indexed_level)
        self.start_urls = UrlsParser.parse(self.start_urls)

        # Build default allowed_domains from start_urls and stop_urls
        if self.allowed_domains is None:
            self.allowed_domains = UrlsParser.build_allowed_domains(self.start_urls, self.stop_urls)

    def update_nb_hits(self, nb_hits):
        if self.config_file is not None:
            # config loaded from file
            previous_nb_hits = None if 'nb_hits' not in self.config_content else self.config_content['nb_hits']
            nb_hit_updater = NbHitsUpdater(self.config_file, self.config_content, previous_nb_hits, nb_hits)
            nb_hit_updater.update()

    def get_extra_facets(self):
        return UrlsParser.get_extra_facets(self.start_urls)
