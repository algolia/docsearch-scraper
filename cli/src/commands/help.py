from abstract_command import AbstractCommand


class Help(AbstractCommand):
    def get_name(self):
        return 'info'

    def get_description(self):
        return 'Get information about docsearch'

    def run(self, args):
        print "Docsearch v1.0"
        return 0
