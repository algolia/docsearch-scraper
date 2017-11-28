from .abstract_command import AbstractCommand


class GenerateComment(AbstractCommand):
    def get_name(self):
        return 'generate:comment'

    def get_description(self):
        return 'Generate the GitHub comment for a docsearch'

    def get_options(self):
        return [{"name": "name", "description": "name of the docsearch you want to generate the comment"}]

    def run(self, args):
        import pyperclip
        from deployer.src.snippeter import get_email_for_config

        self.check_docsearch_app_id('generate a comment')

        comment_content = get_email_for_config(args[0], markdown=true)
        print(comment_content)
        pyperclip.copy(comment_content.replace("\n==============================\n", ''))
        print("Config copied to clipboard [OK]")
        print('')
