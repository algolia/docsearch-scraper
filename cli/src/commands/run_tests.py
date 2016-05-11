from abstract_command import AbstractCommand
from os import getcwd

class RunTests(AbstractCommand):
    def get_name(self):
        return 'test'

    def get_description(self):
        return 'Run tests'

    def run(self, args):
        self.build_docker_file("scraper/dev/docker/Dockerfile.dev")

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
        self.exec_shell_command(run_command)
