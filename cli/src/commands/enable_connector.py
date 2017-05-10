from .abstract_command import AbstractCommand

from deployer.src.helpers import make_request
from deployer.src.fetchers import get_configs_from_website
from deployer.src.helpers import send_slack_notif

from deployer.src.algolia_helper import remove_crawling_issue


class EnableConnector(AbstractCommand):
    def get_name(self):
        return 'connector:enable'

    def get_description(self):
        return 'Disable a connector'

    def get_options(self):
        return [{"name": "name", "description": "name of the connector you want to enable"}]

    def run(self, args):
        configs, inverted, crawler_ids = get_configs_from_website()
        connector_name = args[0]

        make_request('/' + str(inverted[connector_name]) + '/activate', 'PUT')

        send_slack_notif([{
            'title': 'Enable connectors',
            'text': '- ' + connector_name
        }])

