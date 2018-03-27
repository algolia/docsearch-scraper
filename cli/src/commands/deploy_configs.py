from .abstract_command import AbstractCommand


class DeployConfigs(AbstractCommand):
    def get_name(self):
        return 'deploy'

    def get_description(self):
        return 'Deploy configs'

    def run(self, args):
        command = ['./deployer/deploy']
        command = command + args

        return self.exec_shell_command(command)
