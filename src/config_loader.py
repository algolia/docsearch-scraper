import sys
import os.path
import json
import os


class ConfigLoader:
    configs = {}

    def __init__(self):

        self.configs_env = os.environ['CONFIG']

        if self.configs_env is None:
            exit('env `CONFIG` missing')

        config = json.loads(self.configs_env)

        self.configs['app_id'] = self.require_config(os.environ, 'APPLICATION_ID')
        self.configs['api_key'] = self.require_config(os.environ, 'API_KEY')
        self.configs['index_prefix'] = self.require_config(os.environ, 'INDEX_PREFIX')
        self.configs['index_name'] = self.configs['index_prefix'] + self.require_config(config, 'index_name')

        configs_name = ["allowed_domains", "start_urls", "stop_urls",
                        "selectors", "selectors_exclude", "strategy", "custom_settings"]

        for name in configs_name:
            self.configs[name] = self.require_config(config, name)

    def require_config(self, config, name):
        value = config.get(name)

        if value is None:
            print "Needed parameter: '" + name + "'"
            exit()

        return value

    def get_index_name(self):
        return self.configs['index_name']

    def get_allowed_domains(self):
        return self.configs['allowed_domains']

    def get_selectors(self):
        return self.configs['selectors']

    def get_start_urls(self):
        return self.configs['start_urls']

    def get_stop_urls(self):
        return self.configs['stop_urls']

    def get_app_id(self):
        return self.configs['app_id']

    def get_api_key(self):
        return self.configs['api_key']

    def get_strategy(self):
        return self.configs['strategy']

    def get_selectors_exclude(self):
        return self.configs['selectors_exclude']

    def get_custom_settings(self):
        return self.configs['custom_settings']
