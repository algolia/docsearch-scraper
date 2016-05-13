from abstract_command import AbstractCommand
from os import getcwd
from ..helpers import print_error

class RunTests(AbstractCommand):
    def get_name(self):
        return 'test'

    def get_description(self):
        return 'Run tests'

    def get_options(self):
        return [{'name': 'python3', 'description': 'Build the docker image to use python 3 (true|false)'}]

    def run(self, args):
        try:
            py3 = args[0].lower()
            py3[0] = args[0].upper()
            py3 = bool(args[0])
        except ValueError:
            print_error("Invalid value for `python3': {}".format(args[0]))
            return 1

        code = self.build_docker_file("scraper/dev/docker/Dockerfile.dev", python3=py3)
        if code != 0:
            return code

        self.exec_shell_command(["docker", "stop", "documentation-scrapper-dev-test"])
        self.exec_shell_command(["docker", "rm", "documentation-scrapper-dev-test"])

        run_command = [
            'docker',
            'run',
            '-e',
            'APPLICATION_ID=""',
            '-e',
            'API_KEY=""',
            '-e',
            'INDEX_PREFIX=""',
            '-e',
            'CONFIG=""',
            '-v',
            getcwd() + '/scraper/src:/root/src',
            '--name',
            'documentation-scrapper-dev-test',
            '-t',
            'algolia/documentation-scrapper-dev',
            '/root/test'
        ]

        print
        print " ".join(run_command)
        return self.exec_shell_command(run_command)
