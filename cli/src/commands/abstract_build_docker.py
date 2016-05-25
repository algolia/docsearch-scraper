from .abstract_command import AbstractCommand

class AbstractBuildDocker(AbstractCommand):
    def get_options(self):
        return [{'name': 'python3',
                 'description': 'Build the docker image to use python 3 (true|false)',
                 'optional': 'false'}]

    @staticmethod
    def python3_parse(arg):
        if isinstance(arg, bool):
            return arg
        return isinstance(arg, str) and arg.lower() == 'true'

    @staticmethod
    def build_docker_file(file, image="algolia/documentation-scrapper-dev", python3=False):
        cmd = ["docker", "build", "-t", image, "-f", file]
        if not isinstance(python3, bool):
            python3 = isinstance(python3, str) and python3.lower() == 'true'
        if python3:
            cmd.extend(['--build-arg', 'USE_PYTHON3=true'])
        cmd.append('.')
        return AbstractCommand.exec_shell_command(cmd)
