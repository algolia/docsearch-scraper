from abstract_command import AbstractCommand
from os import getcwd


class PlaygroundConfig(AbstractCommand):
    def get_name(self):
        return 'playground'

    def get_description(self):
        return 'Launch the playground'

    def run(self, args):
        # TODO more generic way to get the path
        playground_path = getcwd() + "/playground/index.html"

        self.exec_shell_command(["open", playground_path])
