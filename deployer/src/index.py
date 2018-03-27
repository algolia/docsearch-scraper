import sys
import os

from . import helpers
from .config_manager import ConfigManager

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

config_manager = ConfigManager()

config_name = None
if len(sys.argv) > 1:
    config_name = sys.argv[1]
    from subprocess import check_output
    from os import environ, path

    config_folder = environ.get('PUBLIC_CONFIG_FOLDER')

    if not path.isdir(config_folder):
        print("Folder: " + config_folder + " does not exist")
        exit()

    check_output(['git', 'add', config_name + '.json'], cwd=config_folder)
    check_output(['git', 'commit', '-m', 'update ' + config_name], cwd=config_folder)

    output = check_output(['git', 'stash', 'list'], cwd=config_folder)
    initialNbStash = len(output.split('\n'))
    check_output(['git', 'stash'], cwd=config_folder)
    output2 = check_output(['git', 'stash', 'list'], cwd=config_folder)
    finalNbStash = len(output2.split('\n'))

    check_output(['git', 'pull', '-r', 'origin', 'master'], cwd=config_folder)
    check_output(['git', 'push', 'origin', 'master'], cwd=config_folder)
    if finalNbStash != initialNbStash:
        check_output(['git', 'stash', 'pop'], cwd=config_folder)

added = config_manager.get_added()
changed, changed_attributes = config_manager.get_changed()
removed = config_manager.get_removed()

if config_name is not None:
    if config_name in added:
        changed = []
        removed = []
        added = [config_name]
    elif config_name in changed:
        changed = [config_name]
        removed = []
        added = []
    elif config_name in removed:
        changed = []
        removed = [config_name]
        added = []
    else:
        changed = []
        removed = []
        added = []

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
    if config_name is not None or helpers.confirm() is True:
        reports = []

        if len(added) > 0:
            print("")
            for config_name in added:
                config_manager.add_config(config_name)
            reports.append({ 'title': 'Added connectors', 'text': added_log })

        if len(changed) > 0:
            print("")

            for config_name in changed:
                config_manager.update_config(config_name)
            reports.append({
                'title': 'Updated connectors',
                'text': updated_log
            })

        if len(removed) > 0:
            for config in removed:
                config_manager.remove_config(config_name)

            reports.append({
                'title': 'Removed connectors',
                'text': removed_log
            })
        helpers.send_slack_notif(reports)

else:
    print("Nothing to do")
