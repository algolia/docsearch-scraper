from subprocess import call
from os import environ

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
    def build_docker_file(file, image="algolia/documentation-scrapper-dev", python3=False):
        cmd = ["docker", "build", "-t", image, "-f", file]
        if python3:
            cmd.extend(['--build-arg', 'USE_PYTHON3=true'])
        cmd.append('.')
        return AbstractCommand.exec_shell_command(cmd)

    @staticmethod
    def exec_shell_command(arguments, env=None):
        if env is None:
            env = {}
        merge_env = environ.copy()
        merge_env.update(env)

        return call(arguments, env=merge_env)
