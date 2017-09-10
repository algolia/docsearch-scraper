from .abstract_command import AbstractCommand


class BootstrapConfig(AbstractCommand):
    def get_name(self):
        return 'bootstrap'

    def get_description(self):
        return 'Boostrap a docsearch config'

    def run(self, args):
        from deployer.src.config_creator import create_config
        return create_config()
