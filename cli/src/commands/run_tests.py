from .abstract_command import AbstractCommand


class RunTests(AbstractCommand):
    def get_name(self):
        return "test"

    def get_description(self):
        return "Run tests"

    def run(self, args):
        return self.exec_shell_command(["pytest", "./scraper/src"])
