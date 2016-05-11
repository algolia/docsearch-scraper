from subprocess import call
from os import environ
from helpers import printer

class AbstractCommand(object):
    def run(self, args):
        raise Exception('run need to be implemented')

    def get_name(self):
        raise Exception('get_name need to be implemented')

    def get_description(self):
        raise Exception('get_description need to be implemented')

    def get_usage(self):
        return "  ./docsearch " + self.get_name()

    def get_options(self):
        return []

    @staticmethod
    def build_docker_file(file, image="algolia/documentation-scrapper-dev"):
        AbstractCommand.exec_shell_command(["docker", "build", "-t", image, "-f", file, "."])

    @staticmethod
    def exec_shell_command(arguments, env=None):
        if env is None:
            env = {}
        merge_env = environ.copy()
        merge_env.update(env)

        call(arguments, env=merge_env)
