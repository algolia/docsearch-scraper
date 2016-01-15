# coding: utf-8
"""
Load the config from the CONFIG environment variable
"""
from urlparse import urlparse
import os.path
import json
import os

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
    selectors_exclude = None
    start_urls = None
    stop_urls = None
    strategy = None
    strip_chars = ".,;:§¶"
    min_indexed_level = 0

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
                all_urls = data.get('start_urls', []) + data.get('stop_urls', [])
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

        return data
