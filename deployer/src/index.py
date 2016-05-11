import sys
import os
import itertools

from dict_differ import DictDiffer
import fetchers
import algolia_helper
import helpers
import snippeter
import emails

if 'APPLICATION_ID' not in os.environ or 'API_KEY' not in os.environ or 'WEBSITE_USERNAME' not in os.environ or 'WEBSITE_PASSWORD' not in os.environ:
    print ""
    print "ERROR: missing configuration"
    print ""
    sys.exit(1)

print "\033[0m"
print ""
print "======================="
print "=  Deploy connectors  ="
print "======================="
print ""

ref_configs = fetchers.get_configs_from_repos()
actual_configs, inverted_actual_configs = fetchers.get_configs_from_website()

differ = DictDiffer(ref_configs, actual_configs)

added = differ.added()
removed = differ.removed()
changed, changed_attributes = differ.changed()

if len(added) > 0:
    print ""
    print "Will be added :"
    for config in added:
        print " - " + config

if len(removed) > 0:
    print ""
    print "Will be delete :"
    for config in removed:
        print " - " + config

if len(changed) > 0:
    print ""
    print "Will be updated :"
    for config in changed:
        log = " - " + config + ' (' + ', '.join(changed_attributes[config]) + ')'
        if len(changed_attributes[config]) != 1 or 'nb_hits' not in changed_attributes[config]:
            log = '\033[0;35m' + log + '\033[0m'
        print log

print ""

if len(added) > 0 or len(removed) > 0 or len(changed) > 0:
    if helpers.confirm() is True:
        if len(added) > 0:
            print ""
            for config in added:
                key = algolia_helper.add_docsearch_key(config)
                print config + ' (' + key + ')'
                helpers.make_request('/', 'POST', ref_configs[config])

        if len(changed) > 0:
            print ""

            for config in changed:
                config_id = str(inverted_actual_configs[config])
                key = algolia_helper.get_docsearch_key(config)

                print config + ' (' + key + ')'
                helpers.make_request('/' + config_id, 'PUT', ref_configs[config])
                helpers.make_request('/' + config_id + '/reindex', 'POST', ref_configs[config])

        for config in removed:
            config_id = str(inverted_actual_configs[config])

            helpers.make_request('/' + config_id, 'DELETE')

            algolia_helper.delete_docsearch_key(config)
            algolia_helper.delete_docsearch_index(config)
            algolia_helper.delete_docsearch_index(config + '_tmp')

    if len(added) > 0 or len(changed) > 0:
        print ""
        if helpers.confirm('Do you want to get email templates for added and updated configs (you\'ll need to wait the index creation before pressing enter for it to be correct)'):
            for config in added:
                print snippeter.get_email_for_config(config)
            for config in changed:
                print snippeter.get_email_for_config(config)

        for app in itertools.chain(added, changed):
            if helpers.confirm('\nDo you want to add emails for {}?'.format(app)):
                emails.add(app)

    for app in removed:
        emails.delete(app)
else:
    print "Nothing to do"

