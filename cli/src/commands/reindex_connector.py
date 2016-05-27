from .abstract_command import AbstractCommand
from deployer.src.helpers import make_request
from deployer.src.fetchers import get_configs_from_website


class ReindexConnector(AbstractCommand):
    def get_name(self):
        return 'connector:reindex'

    def get_description(self):
        return 'Reindex a connector'

    def get_usage(self):
        return super(ReindexConnector, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "name", "description": "name of the connector to reindex"}]

    def run(self, args):
        configs, inverted = get_configs_from_website()
        connector_name = args[0]
        make_request('/' + str(inverted[connector_name]) + '/reindex', 'POST')
        return 0

