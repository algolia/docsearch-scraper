from .abstract_command import AbstractCommand


class CheckConfig(AbstractCommand):
    def get_name(self):
        return 'config:check'

    def get_description(self):
        return 'Check the provided config'

    def get_options(self):
        return [{"name": "config", "description": "path to the config to check"}]

    def run(self, args):
        from scraper.src.config.config_loader import ConfigLoader

        try:
            ConfigLoader(args[0])
            print('The provided config is OK!')
        except ValueError as config_error:
            print('The provided config have errors:')
            print(config_error)
