import json
from os import environ

from .abstract_command import AbstractCommand
from ...deployer.helpers import make_custom_get_request
from ...deployer.fetchers import get_configs_from_website


class GetLogs(AbstractCommand):
    def get_name(self):
        return 'connector:logs'

    def get_description(self):
        return 'Reindex a connector'

    def get_usage(self):
        return super(GetLogs, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "name", "description": "name of the connector to reindex"}]

    def run(self, args):
        configs, inverted, crawlers_id = get_configs_from_website()

        connector_name = args[0]

        scheduler_username = environ.get('SCHEDULER_USERNAME')
        scheduler_password = environ.get('SCHEDULER_PASSWORD')

        url = "https://" + scheduler_username + ":" + scheduler_password + "@crawlers.algolia.com/1/crawlers/" + str(crawlers_id[connector_name]) + "/logs"
        r = make_custom_get_request(url)

        logs = json.loads(r.content)['logs']

        for log in reversed(logs):
            print(log['content'])
            print('')

        return 0
