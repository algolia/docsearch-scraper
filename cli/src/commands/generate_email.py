from abstract_command import AbstractCommand

from deployer.src.snippeter import get_email_for_config

class GenerateEmail(AbstractCommand):
    def get_name(self):
        return 'generate:email'

    def get_description(self):
        return 'Generate the email for a docsearch'

    def get_options(self):
        return [{"name": "name", "description": "name of the docsearch you want to generate the email"}]

    def run(self, args):
        print get_email_for_config(args[0])
