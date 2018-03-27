import algoliasearch
import json

from . import algolia_helper
from . import snippeter
from . import emails
from . import helpers
from .dict_differ import DictDiffer
from . import fetchers

from helpdesk_helper import add_note, get_conversation, get_emails_from_conversation, get_conversation_url_from_cuid


class ConfigManager:
    differ = None

    def __init__(self):
        self.ref_configs = fetchers.get_configs_from_repos()
        self.actual_configs, self.inverted_actual_configs, self.crawler_ids = fetchers.get_configs_from_website()

        self.differ = DictDiffer(self.ref_configs, self.actual_configs)

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

        helpers.make_request('/', 'POST', {'configuration': json.dumps(config, separators=(',', ': '))})

        print '\n================================\n'

        if "conversation_id" in config:
            cuid = config["conversation_id"][0]
            add_note(cuid, snippeter.get_email_for_config(config_name))
            conversation = get_conversation(cuid)
            emails_from_conv = get_emails_from_conversation(conversation)
            emails.add(config_name, emails_to_add=emails_from_conv)
            print('Email address fetched and stored, conversation updated and available at {}\n'.format(
                get_conversation_url_from_cuid(cuid)))

        else:
            print(snippeter.get_email_for_config(config_name))
            if helpers.confirm('\nDo you want to add emails for {}?'.format(config_name)):
                emails.add(config_name)

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
                             {'configuration': json.dumps(self.ref_configs[config_name], separators=(',', ': '))})
        helpers.make_request('/' + config_id + '/reindex', 'POST')

        print '\n================================\n'
        print(snippeter.get_email_for_config(config_name))

        if helpers.confirm('\nDo you want to add emails for {}?'.format(config_name)):
            emails.add(config_name)

    def remove_config(self, config_name):
        config_id = str(self.inverted_actual_configs[config_name])

        helpers.make_request('/' + config_id, 'DELETE')

        algolia_helper.delete_docsearch_key(config_name)
        algolia_helper.delete_docsearch_index(config_name)
        algolia_helper.delete_docsearch_index(config_name + '_tmp')

        emails.delete(config_name)
