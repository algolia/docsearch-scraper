"""
Load the config from the CONFIG environment variable
"""
import os.path
import json
import os

class ConfigLoader(object):
    """
    ConfigLoader
    """
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
    strip_chars = None

    def __init__(self):
        if os.environ['CONFIG'] is None:
            exit('env `CONFIG` missing')

        data = json.loads(os.environ['CONFIG'])
        # Merge other ENV variables
        data['app_id'] = os.environ['APPLICATION_ID']
        data['api_key'] = os.environ['API_KEY']
        data['index_prefix'] = os.environ['INDEX_PREFIX']
        data['index_name'] = data['index_prefix'] + data['index_name']

        # List of keys to expose
        public_config_keys = [
            'allowed_domains',
            'api_key',
            'app_id',
            'custom_settings',
            'index_name',
            'index_prefix',
            'selectors',
            'selectors_exclude',
            'start_urls',
            'stop_urls',
            'strategy',
            'strip_chars'
        ]

        # Expose all the data as public attributes
        for name in public_config_keys:
            value = data.get(name)

            if value is None:
                print "Needed parameter: '" + name + "'"
                exit()

            setattr(self, name, data[name])
