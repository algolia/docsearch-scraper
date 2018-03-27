import os
import os.path as path
import subprocess as sp
from collections import OrderedDict
import json

from builtins import input
from . import helpers


def _prompt_command(emails):
    prompt = '===\na <emails>... (add), d <nb> (delete), c <nb> <new> (change), empty to confirm\n> '

    for i, e in enumerate(emails):
        print('{}) {}'.format(i, e))
    ans = input(prompt).strip().split()

    if len(ans) == 0:
        return emails

    if len(ans) < 2:
        print('/!\ Missing number')
        return _prompt_command(emails)

    if ans[0] == 'a':
        emails += ans[1:]
    elif ans[0] == 'c' or ans[0] == 'd':
        try:
            idx = int(ans[1])
        except ValueError:
            print('/!\ Not a valid integer')
            return _prompt_command(emails)
        if idx >= len(emails):
            print('/!\ Out of bounds')
            return _prompt_command(emails)

        if ans[0] == 'd':
            del emails[idx]
        else:
            if len(ans) < 3:
                print('/!\ Missing new email')
                return _prompt_command(emails)
            emails[idx] = ans[2]
    else:
        print('/!\ Invalid command `%s`'.format(' '.join(ans)))
        return _prompt_command(emails)

    return emails


def _retrieve(config_name, config_dir):
    file_path = path.join(config_dir, 'infos', config_name + '.json')

    if path.isfile(file_path):
        with open(file_path, 'r') as f:
            obj = json.loads(f.read())
            return obj['emails']

    return []


def _commit_push(config_name, action, config_dir):
    txt = path.join('infos', config_name + '.json')
    commit_message = 'deploy: {} emails for {}'.format(action, config_name)

    old_dir = os.getcwd()
    os.chdir(config_dir)

    with open(os.devnull, 'w') as dev_null:
        sp.call(['git', 'add', txt], stdout=dev_null, stderr=sp.STDOUT)
        sp.call(['git', 'commit', '-m', commit_message], stdout=dev_null, stderr=sp.STDOUT)
        sp.call(['git', 'push'], stdout=dev_null, stderr=sp.STDOUT)

    os.chdir(old_dir)


def _write(emails, config_name, config_dir):
    file_path = path.join(config_dir, 'infos', config_name + '.json')

    obj = OrderedDict((
        ('name', config_name),
        ('url', ''),
        ('emails', emails),
        ('categories', [])
    ))

    if path.isfile(file_path):
        with open(file_path, 'r') as f:
            obj = json.loads(f.read(), object_pairs_hook=OrderedDict)
            obj['emails'] = emails

    with open(file_path, 'w') as f:
        f.write(json.dumps(obj, separators=(',', ': '), indent=2))


def _prompt_emails(config_name, config_dir):
    emails = _retrieve(config_name, config_dir)

    while True:
        old = emails[:]
        emails = _prompt_command(emails)
        if old == emails:
            break

    return emails


def add(config_name, config_dir=None, emails_to_add=None):
    if config_dir is None:
        config_dir = "/tmp/docsearch-configs-private"

    if emails_to_add and len(emails_to_add) > 0:
        _write(emails_to_add, config_name, config_dir)

    else:
        emails = _prompt_emails(config_name, config_dir)
        _write(emails, config_name, config_dir)

    _commit_push(config_name, 'Update', config_dir)


def delete(config_name, config_dir=None):
    if config_dir is None:
        config_dir = "/tmp/docsearch-configs-private"

    file_path = path.join(config_dir, 'infos', config_name + '.json')
    if path.isfile(file_path) and helpers.confirm('Delete emails for {}'.format(config_name)):
        os.remove(file_path)
        _commit_push(config_name, 'Delete', config_dir)
