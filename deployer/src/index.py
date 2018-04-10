import sys
import os

from . import helpers
from .config_manager import ConfigManager


def print_init():
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


def deploy_config(config_name):
    from subprocess import check_output
    from os import environ, path

    print_init()

    config_folder = environ.get('PUBLIC_CONFIG_FOLDER')
    config_folder += '/configs'

    if not path.isdir(config_folder):
        print("Folder: " + config_folder + " does not exist")
        exit()

    # Not using the config manager to avoid it stashing the config that we want to push
    check_output(['git', 'add', config_name + '.json'], cwd=config_folder)
    check_output(['git', 'commit', '-m', 'update ' + config_name], cwd=config_folder)
    check_output(['git', 'push', 'origin', 'master'], cwd=config_folder)

    config_manager = ConfigManager().instance

    added = config_manager.get_added()
    changed, changed_attributes = config_manager.get_changed()
    removed = config_manager.get_removed()

    if config_name in added:
        deploy_configs([config_name], [], [], changed_attributes, force_deploy=True)
    elif config_name in changed:
        deploy_configs([], [config_name], [], changed_attributes, force_deploy=True)
    elif config_name in removed:
        deploy_configs([], [], [config_name], changed_attributes, force_deploy=True)

    config_manager.destroy()


def deploy():
    print_init()

    config_manager = ConfigManager().instance

    added = config_manager.get_added()
    changed, changed_attributes = config_manager.get_changed()
    removed = config_manager.get_removed()

    deploy_configs(added, changed, removed, changed_attributes)

    config_manager.destroy()


def deploy_configs(added, changed, removed, changed_attributes, force_deploy=False):
    config_manager = ConfigManager().instance

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
        if force_deploy or helpers.confirm() is True:
            reports = []

            if len(added) > 0:
                print("")
                for current_config_name in added:
                    config_manager.add_config(current_config_name)
                reports.append({ 'title': 'Added connectors', 'text': added_log })

            if len(changed) > 0:
                print("")

                for current_config_name in changed:
                    config_manager.update_config(current_config_name)
                reports.append({
                    'title': 'Updated connectors',
                    'text': updated_log
                })

            if len(removed) > 0:
                for current_config_name in removed:
                    config_manager.remove_config(current_config_name)

                reports.append({
                    'title': 'Removed connectors',
                    'text': removed_log
                })
            helpers.send_slack_notif(reports)

    else:
        print("Nothing to do")
