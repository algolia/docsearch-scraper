import sys
import os
import itertools
import algoliasearch
import json

from .dict_differ import DictDiffer
from . import fetchers
from . import algolia_helper
from . import helpers
from . import snippeter
from . import emails
from helpdesk_helper import add_note, get_conversation, get_emails_from_conversation

if 'APPLICATION_ID' not in os.environ or 'API_KEY' not in os.environ or 'WEBSITE_USERNAME' not in os.environ or 'WEBSITE_PASSWORD' not in os.environ:
    print("")
    print("ERROR: missing configuration")
    print("")
    sys.exit(1)

print("\033[0m")
print("")
print("=======================")
print("=  Deploy connectors  =")
print("=======================")
print("")

ref_configs = fetchers.get_configs_from_repos()
actual_configs, inverted_actual_configs, crawler_ids = fetchers.get_configs_from_website()

differ = DictDiffer(ref_configs, actual_configs)

added = differ.added()
removed = differ.removed()
changed, changed_attributes = differ.changed()

added_log = ""
updated_log = ""
removed_log = ""

if len(added) > 0:
    print("")
    print("Will be \033[1;32madded\033[0m :")
    for config in added:
        added_log += " - " + config + "\n"
    print(added_log)

if len(removed) > 0:
    print("")
    print("Will be \033[1;31mdeleted\033[0m :")
    for config in removed:
        removed_log += " - " + config + "\n"
    print(removed_log)

if len(changed) > 0:
    print("")
    print("Will be \033[1;33mupdated\033[0m :")
    for config in changed:
        log = " - " + config + ' (' + ', '.join(changed_attributes[config]) + ')'
        cli_log = log
        if len(changed_attributes[config]) != 1 or 'nb_hits' not in changed_attributes[config]:
            cli_log = '\033[0;35m' + log + '\033[0m'
        updated_log += log + "\n"
        print(cli_log)

print("")

if len(added) > 0 or len(removed) > 0 or len(changed) > 0:

    if helpers.confirm() is True:
        reports = []

        if len(added) > 0:
            print("")
            for config in added:
                key = algolia_helper.add_docsearch_key(config)
                print(config + ' (' + key + ')')
                helpers.make_request('/', 'POST', {'configuration': json.dumps(ref_configs[config], separators=(',', ': '))})
            reports.append({
                'title': 'Added connectors',
                'text': added_log
            })

        if len(changed) > 0:
            print("")

            for config in changed:
                config_id = str(inverted_actual_configs[config])
                message = config

                try:
                    key = algolia_helper.get_docsearch_key(config)
                    message = message + ' (' + key + ')'
                except algoliasearch.helpers.AlgoliaException:
                    pass

                print(message)

                helpers.make_request('/' + config_id, 'PUT', {'configuration': json.dumps(ref_configs[config], separators=(',', ': '))})
                helpers.make_request('/' + config_id + '/reindex', 'POST')
            reports.append({
                'title': 'Updated connectors',
                'text': updated_log
            })

        if len(removed) > 0:
            for config in removed:
                config_id = str(inverted_actual_configs[config])

                helpers.make_request('/' + config_id, 'DELETE')

                algolia_helper.delete_docsearch_key(config)
                algolia_helper.delete_docsearch_index(config)
                algolia_helper.delete_docsearch_index(config + '_tmp')

            reports.append({
                'title': 'Removed connectors',
                'text': removed_log
            })
        helpers.send_slack_notif(reports)

    if len(added) > 0 or len(changed) > 0:
        print("")

        if helpers.confirm('Do you want to get & save as a note the email templates for added configs (you\'ll need to wait the index creation before pressing enter for it to be correct)'):

            for config in added:
                print '\n================================\n'

                print(snippeter.get_email_for_config(config))
                emails_from_conv = None

                if "conversation_id" in ref_configs[config]:
                    cuid=ref_configs[config]["conversation_id"][0]
                    add_note(cuid, snippeter.get_email_for_config(config))
                    conversation = get_conversation(cuid)
                    emails_from_conv = get_emails_from_conversation(conversation)

                if helpers.confirm('\nDo you want to add emails for {}?'.format(config)):
                    emails.add(config,
                               emails_to_add = emails_from_conv)

            for config in changed:
                print '\n================================\n'
                print(snippeter.get_email_for_config(config))
                if helpers.confirm('\nDo you want to add emails for {}?'.format(config)):
                    emails.add(config)

    for app in removed:
        emails.delete(app)
else:
    print("Nothing to do")
