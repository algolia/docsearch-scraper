from .abstract_command import AbstractCommand


class ReindexConnector(AbstractCommand):
    def get_name(self):
        return "connector:reindex"

    def get_description(self):
        return "Reindex a connector"

    def get_usage(self):
        return super(ReindexConnector, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "name",
                 "description": "name of the connector to reindex"}]

    def run(self, args):
        from deployer.src.helpers import make_request
        from deployer.src.fetchers import get_configs_from_website
        from deployer.src.helpers import send_slack_notif

        configs, inverted, crawler_ids = get_configs_from_website()
        connector_name = args[0]
        make_request('/{}/reindex'.format(inverted[connector_name]), "POST")

        send_slack_notif([{
            "title": "Manually reindexed connectors",
            "text": "- " + connector_name
        }])

        return 0
