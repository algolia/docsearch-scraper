from abstract_command import AbstractCommand


class InstallDependencies(AbstractCommand):
    def get_name(self):
        return 'requirements:install'

    def get_description(self):
        return 'Install all dependencies needed to administrate docsearch'

    def run(self, args):
        self.exec_shell_command(["pip", "install", "-r", "requirements.txt"])
