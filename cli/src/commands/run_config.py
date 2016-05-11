from abstract_command import AbstractCommand
from os import environ

class RunConfig(AbstractCommand):
    def get_name(self):
        return 'config:run'

    def get_description(self):
        return 'Run a config'

    def get_usage(self):
        return super(RunConfig, self).get_usage() + " config"

    def get_options(self):
        return [{"name": "config", "description": "path to the config to run"}]

    def run(self, args):
        run_command = ["python", "scraper/src/index.py"]
        env = environ.copy()
        env.update({'CONFIG': args[0], 'INDEX_PREFIX': ""})

        self.exec_shell_command(run_command, env)
