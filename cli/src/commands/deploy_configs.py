from .abstract_command import AbstractCommand
from os import environ

class DeployConfigs(AbstractCommand):
    def get_name(self):
        return 'deploy:configs'

    def get_description(self):
        return 'Deploy configs'

    def run(self, args):
        self.check_docsearch_app_id('deploy configs')

        command = ['./deployer/deploy']

        if len(args) > 0 and args[0] == '--debug':
            command.append('--debug')

        return self.exec_shell_command(command)
