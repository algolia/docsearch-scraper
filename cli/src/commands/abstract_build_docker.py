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
    def build_docker_file(file, image="algolia/documentation-scraper-dev"):
        cmd = ["docker", "build", "-t", image, "-f", file, "."]
        return AbstractCommand.exec_shell_command(cmd)
