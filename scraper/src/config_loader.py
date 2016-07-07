# coding: utf-8
"""
Load the config from the CONFIG environment variable
"""

from __future__ import absolute_import

from collections import OrderedDict
from past.builtins import basestring
import json
import os
import re
import copy

from selenium import webdriver

try:
    from strategies.abstract_strategy import AbstractStrategy
    from custom_middleware import CustomMiddleware
    from js_executor import JsExecutor
    from selenium import webdriver
    import helpers
except ImportError:
    from .strategies.abstract_strategy import AbstractStrategy
    from .custom_middleware import CustomMiddleware
    from .js_executor import JsExecutor
    from . import helpers

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

class ConfigLoader(object):
    """
    ConfigLoader
    """
    # We define them here so the linters/autocomplete know what to expect
    allowed_domains = None
    api_key = None
    app_id = None
    custom_settings = None
    index_name = None
    index_prefix = None
    selectors = None
    selectors_exclude = []
    start_urls = None
    stop_urls = []
    strategy = None
    strip_chars = u".,;:§¶"
    min_indexed_level = 0
    scrap_start_urls = True
    strict_redirect = False
    remove_get_params = False

    # data storage, starting here attribute are not config params
    config_file = None
    config_content = None
    config_original_content = None

    driver = None

    def __init__(self):
        if os.environ['CONFIG'] is '':
            exit('env `CONFIG` missing')

        config = os.environ['CONFIG']

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

        # Check for all mandatory variables
        data = self.assert_config(data)

        # Merge other ENV variables
        data['app_id'] = os.environ['APPLICATION_ID']
        data['api_key'] = os.environ['API_KEY']
        data['index_prefix'] = os.environ['INDEX_PREFIX']

        # Expose all the data as attributes
        data['index_name'] = data['index_prefix'] + data['index_name']
        for key, value in data.items():
            setattr(self, key, value)

        if self.conf_need_browser():
            self.init()

        self.start_urls = self.parse_urls(self.start_urls)
        self.selectors = self.parse_selectors(self.selectors)

        if self.conf_need_browser() and not self.js_render:
            self.destroy()

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

    @staticmethod
    def parse_selectors_set(config_selectors):
        selectors_set = {}
        for key in config_selectors:
            if key != 'text':
                selectors_set[key] = config_selectors[key]
            else:
                # Backward compatibility, rename text to content
                key = 'content'
                selectors_set[key] = config_selectors['text']

            # Backward compatibility, if it's a string then we put it in an object
            if isinstance(selectors_set[key], basestring):
                selectors_set[key] = {'selector': selectors_set[key]}

            # Global
            if 'global' in selectors_set[key]:
                selectors_set[key]['global'] = bool(selectors_set[key]['global'])
            else:
                selectors_set[key]['global'] = False

            # Type
            if 'type' in selectors_set[key]:
                if selectors_set[key]['type'] not in ['xpath', 'css']:
                    raise Exception(
                        selectors_set[key]['type'] + 'is not a good selector type, it should be `xpath` or `css`')
            else:
                selectors_set[key]['type'] = 'css'

            if selectors_set[key]['type'] == 'css':
                selectors_set[key]['selector'] = AbstractStrategy.css_to_xpath(selectors_set[key]['selector'])

            # We don't need it because everything is xpath now
            selectors_set[key].pop('type')

            # Default value
            selectors_set[key]['default_value'] = selectors_set[key]['default_value'] if 'default_value' in selectors_set[
                key] else None

            # Strip chars
            selectors_set[key]['strip_chars'] = selectors_set[key]['strip_chars'] if 'strip_chars' in selectors_set[key] else None

        return selectors_set

    @staticmethod
    def parse_selectors(config_selectors):
        selectors = {}

        if 'lvl0' in config_selectors:
            config_selectors = {'default': config_selectors}

        for selectors_key in config_selectors:
            selectors[selectors_key] = ConfigLoader.parse_selectors_set(config_selectors[selectors_key])

        return selectors

    def get_extra_facets(self):
        extra_facets = []
        for start_url in self.start_urls:
            for tag in start_url['url_attributes']:
                extra_facets.append(tag)

        extra_facets = set(extra_facets)

        return list(extra_facets)

    @staticmethod
    def parse_urls(config_start_urls):
        start_urls = []
        for start_url in config_start_urls:
            if isinstance(start_url, basestring):
                start_url = {'url': start_url}

            start_url['compiled_url'] = re.compile(start_url['url'])

            if "page_rank" not in start_url:
                start_url['page_rank'] = 0

            if "tags" not in start_url:
                start_url['tags'] = []

            if "selectors_key" not in start_url:
                start_url['selectors_key'] = 'default'

            matches = ConfigLoader.get_url_variables_name(start_url['url'])

            start_url['url_attributes'] = {}
            for match in matches:
                if len(start_url['url']) > 2 and start_url['url'][-2:] == '?)':
                    print('\033[0;35mWARNING: ' + start_url['url'] + ' finish by a variable.'
                                                           ' The regex probably won\'t work as expected.'
                                                           ' Add a \'/\' or \'$\' to make it work properly\033[0m')
                start_url['url_attributes'][match] = None

            # If there is tag(s) we need to generate all possible urls
            if len(matches) > 0:
                values = {}
                for match in matches:
                    if 'variables' in start_url:
                        if match in start_url['variables']:
                            if isinstance(start_url['variables'][match], list):
                                values[match] = start_url['variables'][match]
                            else:
                                if 'url' in start_url['variables'][match] and 'js' in start_url['variables'][match]:
                                    executor = JsExecutor()
                                    values[match] = executor.execute(start_url['variables'][match]['url'], start_url['variables'][match]['js'])
                                else:
                                    raise Exception("Bad arguments for variables." + match + " for url " + start_url['url'])
                        else:
                            raise Exception("Missing " + match + " in variables" + " for url " + start_url['url'])

                start_urls = ConfigLoader.geturls(start_url, matches[0], matches[1:], values, start_urls)

            # If there is no tag just keep it like this
            else:
                start_urls.append(start_url)

        return start_urls

    @staticmethod
    def get_url_variables_name(url):
        # Cache it to avoid to compile it several time
        if not hasattr(ConfigLoader.get_url_variables_name, 'group_regex'):
            ConfigLoader.get_url_variables_name.group_regex = re.compile("\\(\?P<(.+?)>.+?\\)")

        return re.findall(ConfigLoader.get_url_variables_name.group_regex, url)

    @staticmethod
    def geturls(start_url, current_match, matches, values, start_urls):
        for value in values[current_match]:
            copy_start_url = copy.copy(start_url)
            copy_start_url['url'] = copy_start_url['url'].replace("(?P<"+current_match+">.*?)", value)
            copy_start_url['compiled_url'] = re.compile(copy_start_url['url'])
            # Fix weird reference issue
            copy_start_url['url_attributes'] = copy.deepcopy(start_url['url_attributes'])
            copy_start_url['url_attributes'][current_match] = value

            if len(matches) == 0:
                start_urls.append(copy_start_url)
            else:
                start_urls = ConfigLoader.geturls(copy_start_url, matches[0], matches[1:], values, start_urls)

        return start_urls

    @staticmethod
    def assert_config(user_data):
        """Check for all needed parameters in config"""

        # Set default values
        default_data = {
            'start_urls': [],
            'stop_urls': []
        }
        data = default_data.copy()
        data.update(user_data)

        if not data.get('index_name'):
            raise ValueError('index_name is not defined')

        # Start_urls is mandatory
        if not data.get('start_urls'):
            raise ValueError('start_urls is not defined')

        # Start urls must be an array
        if not isinstance(data.get('start_urls'), list):
            data['start_urls'] = [data['start_urls']]

        # Stop urls must be an array
        if not isinstance(data.get('stop_urls'), list):
            data['stop_urls'] = [data['stop_urls']]

        # Build default allowed_domains from start_urls and stop_urls
        if not data.get('allowed_domains'):
            if not data.get('allowed_domains'):
                def get_domain(url):
                    """ Return domain name from url """
                    return urlparse(url).netloc

                # Concatenating both list, being careful that they can be None
                all_urls = [_['url'] if not isinstance(_, basestring) else _ for _ in data.get('start_urls', [])] + data.get('stop_urls', [])
                # Getting the list of domains for each of them
                all_domains = [get_domain(_) for _ in all_urls]
                # Removing duplicates
                all_domains_unique = []
                for domain in all_domains:
                    if domain in all_domains_unique:
                        continue
                    all_domains_unique.append(domain)

                data['allowed_domains'] = all_domains_unique

        # Allowed domains must be an array
        if not isinstance(data.get('allowed_domains'), list):
            data['allowed_domains'] = [data['allowed_domains']]

        # Set default strategy
        data['strategy'] = data.get('strategy') or 'default'

        # `js_render` is set to False by default unless `true` is specified
        if isinstance(data.get('js_render'), bool):
            data['js_render'] = data.get('js_render')
        else:
            data['js_render'] = False

        # `js_wait` is set to 0s by default unless it is specified
        if isinstance(data.get('js_wait'), int):
            data['js_wait'] = data.get('js_wait')
        else:
            data['js_wait'] = 0

        # `use_anchors` is set to True by default unless `false` is specified
        if isinstance(data.get('use_anchors'), bool):
            data['use_anchors'] = data.get('use_anchors')
        else:
            data['use_anchors'] = False

        return data

    def update_nb_hits(self, nb_hits):
        if self.config_file is not None:
            previous_nb_hits = None if 'nb_hits' not in self.config_content else self.config_content['nb_hits']

            if previous_nb_hits is None or previous_nb_hits != nb_hits:
                print( "previous nb_hits: " + str(previous_nb_hits))
                print("")

                if helpers.confirm('Do you want to update the nb_hits in ' + self.config_file + ' ?'):
                    try:
                        self.config_content['nb_hits'] = nb_hits
                        with open(self.config_file, 'w') as f:
                            f.write(json.dumps(self.config_content, indent=2, separators=(',', ': ')))
                        print("")
                        print("[OK] " + self.config_file + " has been updated")
                    except Exception:
                        print("")
                        print("[KO] " + "Was not able to update " + self.config_file)
