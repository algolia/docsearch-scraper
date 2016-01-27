# coding: utf-8
"""
Load the config from the CONFIG environment variable
"""
from urlparse import urlparse
from strategies.abstract_strategy import AbstractStrategy
import json
import os
import re

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
    compiled_start_urls = []
    stop_urls = None
    strategy = None
    strip_chars = u".,;:§¶"
    min_indexed_level = 0
    urls = None

    def __init__(self):
        if os.environ['CONFIG'] is '':
            exit('env `CONFIG` missing')

        try:
            data = json.loads(os.environ['CONFIG'])
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
        for key, value in data.iteritems():
            setattr(self, key, value)

        self.start_urls = self.parse_urls(self.start_urls)
        self.selectors = self.parse_selectors(self.selectors)

    @staticmethod
    def parse_selectors(config_selectors):
        selectors = {}

        for key in config_selectors:
            if key != 'text':
                selectors[key] = config_selectors[key]
            else:
                # Backward compatibility, rename text to content
                key = 'content'
                selectors[key] = config_selectors['text']

            # Backward compatibility, if it's a string then we put it in an object
            if isinstance(selectors[key], basestring):
                selectors[key] = {'selector': selectors[key]}

            # Global
            if 'global' in selectors[key]:
                selectors[key]['global'] = bool(selectors[key]['global'])
            else:
                selectors[key]['global'] = False

            # Type
            if 'type' in selectors[key]:
                if selectors[key]['type'] not in ['xpath', 'css']:
                    raise Exception(selectors[key]['type'] + 'is not a good selector type, it should be `xpath` or `css`')
            else:
                selectors[key]['type'] = 'css'

            if selectors[key]['type'] == 'css':
                selectors[key]['selector'] = AbstractStrategy.css_to_xpath(selectors[key]['selector'])

            # We don't need it because everything is xpath now
            selectors[key].pop('type')

            # Default value
            selectors[key]['default_value'] = selectors[key]['default_value'] if 'default_value' in selectors[key] else None

            # Strip chars
            selectors[key]['strip_chars'] = selectors[key]['strip_chars'] if 'strip_chars' in selectors[key] else None

            # Searchable
            selectors[key]['searchable'] = bool(selectors[key]['searchable']) if 'searchable' in selectors[key] else True

        return selectors

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

            start_urls.append(start_url)

        return start_urls

    @staticmethod
    def assert_config(user_data):
        """Check for all needed parameters in config"""

        # Set default values
        default_data = {
            'start_urls': [],
            'stop_url': []
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

        # `js_wait` is set to 0.5 by default it is specified
        if isinstance(data.get('js_wait'), float):
            data['js_wait'] = data.get('js_wait')
        else:
            data['js_wait'] = 0.5

        # `use_anchors` is set to True by default unless `false` is specified
        if isinstance(data.get('use_anchors'), bool):
            data['use_anchors'] = data.get('use_anchors')
        else:
            data['use_anchors'] = True

        return data
