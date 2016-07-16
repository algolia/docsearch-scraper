import pyperclip

from .abstract_command import AbstractCommand
from ...deployer.snippeter import get_email_for_config


class GenerateEmail(AbstractCommand):
    def get_name(self):
        return 'generate:email'

    def get_description(self):
        return 'Generate the email for a docsearch'

    def get_options(self):
        return [{"name": "name", "description": "name of the docsearch you want to generate the email"}]

    def run(self, args):
        self.check_docsearch_app_id('generate an email')

        email_content = get_email_for_config(args[0])
        print(email_content)
        pyperclip.copy(email_content.replace("\n==============================\n", ''))
        print("Config copied to clipboard [OK]")
        print('')
