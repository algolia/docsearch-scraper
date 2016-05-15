from abstract_command import AbstractCommand


class BootstrapConfig(AbstractCommand):
    def get_name(self):
        return 'config:bootstrap'

    def get_description(self):
        return 'Boostrap a docsearch config'

    def run(self, args):
        self.exec_shell_command(["python", "deployer/src/config_creator.py"])
