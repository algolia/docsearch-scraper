from .abstract_command import AbstractCommand


class RunConfigDocker(AbstractCommand):
    def get_name(self):
        return 'docker:run'

    def get_description(self):
        return 'Run a config using docker'

    def get_usage(self):
        return super(RunConfigDocker, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "config", "description": "path to the config to run"}]

    def run(self, args):
        from os import getcwd, environ

        self.check_not_docsearch_app_id('run a config manually')

        self.exec_shell_command(["docker", "stop", "documentation-scrapper-dev"])
        self.exec_shell_command(["docker", "rm", "documentation-scrapper-dev"])

        f = open(args[0], 'r')
        config = f.read()

        run_command = [
            'docker',
            'run',
            '-e',
            'APPLICATION_ID=' + environ.get('APPLICATION_ID'),
            '-e',
            'API_KEY=' + environ.get('API_KEY'),
            '-e',
            "CONFIG=" + config,
            '-v',
            getcwd() + '/scraper/src:/root/src',
            '--name',
            'documentation-scrapper-dev',
            '-t',
            'algolia/documentation-scrapper-dev',
            '/root/run'
        ]

        return self.exec_shell_command(run_command)
