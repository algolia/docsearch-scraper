from subprocess import call
from os import environ

class AbstractCommand(object):
    def run(self, args):
        raise Exception('run need to be implemented')

    def get_name(self):
        raise Exception('get_name need to be implemented')

    def get_description(self):
        raise Exception('get_description need to be implemented')

    def get_usage(self):
        return "  ./docsearch " + self.get_name()

    def get_options(self):
        return []

    def nb_options(self):
        return len(list(filter(lambda x: x.get('optional') is None,
                          self.get_options())))

    def get_option(self, name, args):
        options = self.get_options()
        index = [i for i, j in enumerate(options) if j['name'] == name]
        if len(index) == 0:
            return None
        else:
            index = index[0]

        if index < len(args):
            return args[index]
        else:
            return options[index]['optional']

    @staticmethod
    def exec_shell_command(arguments, env=None):
        if env is None:
            env = {}
        merge_env = environ.copy()
        merge_env.update(env)

        return call(arguments, env=merge_env)
