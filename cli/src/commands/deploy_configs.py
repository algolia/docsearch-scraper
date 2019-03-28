from .abstract_command import AbstractCommand


class DeployConfigs(AbstractCommand):
    def get_name(self):
        return "deploy"

    def get_description(self):
        return "Deploy configs"

    def run(self, args):
        if len(args) <= 0:
            from deployer.src.index import deploy
            deploy()
        else:
            from deployer.src.index import deploy_config
            deploy_config(unicode(args[0]))
