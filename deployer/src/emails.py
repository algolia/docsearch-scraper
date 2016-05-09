import os
import os.path as path
import subprocess as sp

import helpers


def _prompt_command(emails):
    prompt = '===\na <emails>... (add), d <nb> (delete), c <nb> <new> (change), empty to confirm\n> '

    for i, e in enumerate(emails):
        print '{}) {}'.format(i, e)
    ans = raw_input(prompt).strip().split()

    if len(ans) == 0:
        return emails

    if len(ans) < 2:
        print '/!\ Missing number'
        return _prompt_command(emails)

    if ans[0] == 'a':
        emails += ans[1:]
    elif ans[0] == 'c' or ans[0] == 'd':
        try:
            idx = int(ans[1])
        except ValueError:
            print '/!\ Not a valid integer'
            return _prompt_command(emails)
        if idx >= len(emails):
            print '/!\ Out of bounds'
            return _prompt_command(emails)

        if ans[0] == 'd':
            del emails[idx]
        else:
            if len(ans) < 3:
                print '/!\ Missing new email'
                return _prompt_command(emails)
            emails[idx] = ans[2]
    else:
        print '/!\ Invalid command `%s`'.format(' '.join(ans))
        return _prompt_command(emails)

    return emails


def _retrieve(config_name):
    base_dir = path.dirname(__file__)
    txt = path.join(base_dir, '..', 'private', 'infos', config_name + '.txt')
    if path.isfile(txt):
        with open(txt, 'r') as f:
            return [l.strip() for l in f.readlines()]
    return []


def _commit_push(config_name, action):
    dir_ = path.join(path.dirname(__file__), '..', 'private')
    txt = path.join('infos', config_name + '.txt')
    commit_message = 'deploy: {} emails for {}'.format(action, config_name)

    old_dir = os.getcwd()
    os.chdir(dir_)

    with open(os.devnull, 'w') as dev_null:
        sp.call(['git', 'add', txt], stdout=dev_null, stderr=sp.STDOUT)
        sp.call(['git', 'commit', '-m', commit_message], stdout=dev_null, stderr=sp.STDOUT)
        sp.call(['git', 'push'], stdout=dev_null, stderr=sp.STDOUT)

    os.chdir(old_dir)


def _write(emails, config_name):
    base_dir = path.dirname(__file__)
    txt = path.join(base_dir, '..', 'private', 'infos', config_name + '.txt')
    with open(txt, 'w') as f:
        f.write('\n'.join(emails))


def _prompt_emails(config_name):
    emails = _retrieve(config_name)

    while True:
        old = emails[:]
        emails = _prompt_command(emails)
        if old == emails:
            break

    return emails


def add(config_name):
    emails = _prompt_emails(config_name)
    _write(emails, config_name)
    _commit_push(config_name, 'Update')


def delete(config_name):
    base_dir = path.dirname(__file__)
    txt = path.join(base_dir, '..', 'private', 'infos', config_name + '.txt')
    if path.isfile(txt) and helpers.confirm('Delete emails for {}'.format(config_name)):
        os.remove(txt)
        _commit_push(config_name, 'Delete')
