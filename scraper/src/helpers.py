from builtins import input
from cssselect import HTMLTranslator


def confirm(message="Confirm"):
    prompt = message + ' [y/n]:\n'

    while True:
        ans = input(prompt)
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def css_to_xpath(css):
    return HTMLTranslator().css_to_xpath(css) if len(css) > 0 else ""
