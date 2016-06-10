import os
from os import path
import subprocess as sp

from .abstract_command import AbstractCommand

from deployer.src.emails import add, delete


def _ensure_configs_private():
    # Check the presence of configs-private or clone it.
    p = '/tmp/docsearch_deploy/scraper/deployer'
    try:
        os.makedirs(p)
    except OSError:
        pass
    old_dir = os.getcwd()
    os.chdir(p)
    if not path.isdir('private'):
        sp.call(['git', 'clone', '--depth', '1', '--branch', 'master',
                 'git@github.com:algolia/docsearch-configs-private.git',
                 'private'])
    os.chdir(old_dir)
    return p


class UpdateEmails(AbstractCommand):
    def get_name(self):
        return 'emails:update'

    def get_description(self):
        return 'Add or update contact emails'

    def get_options(self):
        return [{'name': 'configs...', 'description': 'name of the docsearch you want to update contact emails'}]

    def run(self, args):
        p = _ensure_configs_private()
        for config in args:
            add(config, path.join(p, 'private'))


class DeleteEmails(AbstractCommand):
    def get_name(self):
        return 'emails:delete'

    def get_description(self):
        return 'Delete contact emails'

    def get_options(self):
        return [{'name': 'configs...', 'description': 'name of the docsearch you want to delete contact emails'}]

    def run(self, args):
        p = _ensure_configs_private()
        for config in args:
            delete(config,  path.join(p, 'private'))

