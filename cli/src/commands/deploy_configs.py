from .abstract_command import AbstractCommand
from os import environ

class DeployConfigs(AbstractCommand):
    def get_name(self):
        return 'deploy:configs'

    def get_description(self):
        return 'Deploy configs'

    def run(self, args):
        if environ.get('APPLICATION_ID') != 'BH4D9OD16A':
            print("The APP_ID is not BH4D9OD16A. You can not deploy configs if you are not using the docsearch account")
            exit(1)

        return self.exec_shell_command(['./deployer/deploy'])
