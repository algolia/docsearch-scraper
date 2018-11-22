from .abstract_command import AbstractCommand
import os


class RunConfigDocker(AbstractCommand):
    def get_name(self):
        return 'docker:run'

    def get_description(self):
        return 'Run a config using docker'

    def get_usage(self):
        return super(RunConfigDocker, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "config",
                 "description": "path to the config to run from the remote docker image"},
                {"name": "from_local_code",
                 "description": "use the local code to run the crawl",
                 'optional': False}]

    @staticmethod
    def from_local_code_parse(args):
        print(args)
        if len(args) < 2:
            return False
        if isinstance(args[1], bool):
            return args[1]
        return isinstance(args[1], str) and args[1].lower() == 'true'

    def run(self, args):

        self.check_not_docsearch_app_id('run a config manually')

        if os.path.isfile(args[0]):
            f = open(args[0], 'r')
            config = f.read()
        else:
            raise ValueError(
                "Config option: {} is not a path to a file".format(args[0]))

        from_local_code = self.get_option('from_local_code', args)

        run_command = []
        if not from_local_code:
            run_command = [
                'docker',
                'run',
                '--rm',
                '-e',
                'APPLICATION_ID=' + os.environ.get('APPLICATION_ID'),
                '-e',
                'API_KEY=' + os.environ.get('API_KEY'),
                '-e',
                "CONFIG=" + config,
                '--name',
                'documentation-scraper',
                '-t',
                'algolia/documentation-scraper',
                '-i',
                '/root/run'
            ]
        else:
            run_command = [
                'docker',
                'run',
                '--rm',
                '-e',
                'APPLICATION_ID=' + os.environ.get('APPLICATION_ID'),
                '-e',
                'API_KEY=' + os.environ.get('API_KEY'),
                '-e',
                "CONFIG=" + config,
                '-v',
                os.getcwd() + '/scraper/src:/root/src',
                '--name',
                'documentation-scraper-dev',
                '-t',
                'algolia/documentation-scraper-dev',
                '/root/run'
            ]
        return self.exec_shell_command(run_command)
