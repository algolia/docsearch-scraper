import algoliasearch
import json
from os import environ
from subprocess import check_output

from . import algolia_helper
from . import snippeter
from . import emails
from . import helpers
from .dict_differ import DictDiffer
from . import fetchers

from helpdesk_helper import add_note, get_conversation, \
    get_emails_from_conversation, get_conversation_url_from_cuid

from deployer.src.algolia_internal_api import remove_user_from_index


class ConfigManager:
    instance = None

    def __init__(self):
        if not ConfigManager.instance:
            ConfigManager.instance = ConfigManager.__ConfigManager()

    class __ConfigManager:
        def __init__(self):
            self.public_dir = environ.get('PUBLIC_CONFIG_FOLDER')
            self.private_dir = environ.get('PRIVATE_CONFIG_FOLDER')

            if self.public_dir is None or self.private_dir is None:
                print(
                    'PUBLIC_CONFIG_FOLDER and PRIVATE_CONFIG_FOLDER must be defined in the environment')
                exit()

            self.initial_public_nb_stash = None
            self.final_nb_public_stash = None
            self.initial_private_nb_stash = None
            self.final_nb_private_stash = None

            self.init()

            self.ref_configs = fetchers.get_configs_from_repos()
            self.actual_configs, self.inverted_actual_configs, self.crawler_ids = fetchers.get_configs_from_website()

            self.differ = DictDiffer(self.ref_configs, self.actual_configs)

        def init(self):
            output = check_output(['git', 'stash', 'list'],
                                  cwd=self.public_dir)
            self.initial_public_nb_stash = len(output.split('\n'))
            check_output(['git', 'stash', '--include-untracked'],
                         cwd=self.public_dir)
            output2 = check_output(['git', 'stash', 'list'],
                                   cwd=self.public_dir)
            self.final_nb_public_stash = len(output2.split('\n'))
            check_output(['git', 'pull', '-r', 'origin', 'master'],
                         cwd=self.public_dir)

            output = check_output(['git', 'stash', 'list'],
                                  cwd=self.private_dir)
            self.initial_private_nb_stash = len(output.split('\n'))
            check_output(['git', 'stash', '--include-untracked'],
                         cwd=self.private_dir)
            output2 = check_output(['git', 'stash', 'list'],
                                   cwd=self.private_dir)
            self.final_nb_private_stash = len(output2.split('\n'))
            check_output(['git', 'pull', '-r', 'origin', 'master'],
                         cwd=self.private_dir)

        def destroy(self):
            if self.final_nb_public_stash != self.initial_public_nb_stash:
                check_output(['git', 'stash', 'pop'], cwd=self.public_dir)

            if self.final_nb_private_stash != self.initial_private_nb_stash:
                check_output(['git', 'stash', 'pop'], cwd=self.private_dir)

        def get_configs_from_repos(self):
            fetchers.get_configs_from_repos()

        def get_configs_from_website(self):
            fetchers.get_configs_from_website()

        differ = None
        public_dir = None
        private_dir = None

        def get_added(self):
            return self.differ.added()

        def get_removed(self):
            return self.differ.removed()

        def get_changed(self):
            return self.differ.changed()

        def add_config(self, config_name):
            key = algolia_helper.add_docsearch_key(config_name)

            print(config_name + ' (' + key + ')')
            config = self.ref_configs[config_name]

            helpers.make_request('/', 'POST', {
                'configuration': json.dumps(config, separators=(',', ': '))})

            print('\n================================\n')

            if "conversation_id" in config:
                cuid = config["conversation_id"][0]

                # Add email(s) to the private config & grant access
                conversation = get_conversation(cuid)
                emails_from_conv = get_emails_from_conversation(conversation)
                analytics_statuses = emails.add(config_name, self.private_dir,
                                                emails_to_add=emails_from_conv)

                note_content = snippeter.get_email_for_config(config_name,
                                                              analytics_statuses)

                add_note(cuid, note_content)

                print(
                    'Email address fetched and stored, conversation updated and available at {}\n'.format(
                        get_conversation_url_from_cuid(cuid)))

            else:
                if helpers.confirm(
                        '\nDo you want to add emails for {}?'.format(
                                config_name)):
                    analytics_statuses = emails.add(config_name,
                                                    self.private_dir)
                    print(snippeter.get_email_for_config(config_name,
                                                         analytics_statuses))
                else:
                    print(snippeter.get_email_for_config(config_name))

        def update_config(self, config_name):
            config_id = str(self.inverted_actual_configs[config_name])
            message = config_name

            try:
                key = algolia_helper.get_docsearch_key(config_name)
                message = message + ' (' + key + ')'
            except algoliasearch.helpers.AlgoliaException:
                pass

            print(message)

            helpers.make_request('/' + config_id, 'PUT',
                                 {'configuration': json.dumps(
                                     self.ref_configs[config_name],
                                     separators=(',', ': '))})
            helpers.make_request('/' + config_id + '/reindex', 'POST')

            print('\n================================\n')
            print(snippeter.get_email_for_config(config_name))

            if helpers.confirm(
                    '\nDo you want to add emails for {}?'.format(config_name)):
                emails.add(config_name, self.private_dir)

        def remove_config(self, config_name):
            config_id = str(self.inverted_actual_configs[config_name])

            helpers.make_request('/' + config_id, 'DELETE')

            algolia_helper.delete_docsearch_key(config_name)
            algolia_helper.delete_docsearch_index(config_name)
            algolia_helper.delete_docsearch_index(config_name + '_tmp')
            analytics_keys = algolia_helper.list_index_analytics_key(
                config_name)
            for key in analytics_keys:
                description = key['description'].split()
                email = description[4]
                print(email)
                if email is not None:
                    remove_user_from_index(config_name, email)

            emails.delete(config_name, self.private_dir)
