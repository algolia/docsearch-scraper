from .abstract_build_docker import AbstractBuildDocker
from os import getcwd
from ..helpers import print_error

class RunTests(AbstractBuildDocker):
    def get_name(self):
        return 'test'

    def get_description(self):
        return 'Run tests'

    def run(self, args):
        py3 = self.get_option('python3', args)
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

        print("")
        print(" ".join(run_command))
        return self.exec_shell_command(run_command)
