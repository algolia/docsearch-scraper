import os
import requests
import json

username = os.environ['WEBSITE_USERNAME'] if 'WEBSITE_USERNAME' in os.environ else ''
password = os.environ['WEBSITE_PASSWORD'] if 'WEBSITE_PASSWORD' in os.environ else ''

base_url = 'https://www.algolia.com/api/1/docsearch'

def get_color(color=4):
    if color == 1:
        return "\033[0;32m"
    elif color == 2:
        return "\033[33m"
    elif color == 3:
        return "\033[1;33m\033[1;41m"
    else:
        return "\033[0m"

def printer(text, color = 4):
    print get_color(color) + text + get_color()

def print_error(message):
    line = " " * (len(message) + 4)
    printer(line, 3)
    printer(" " * 2 + message + " " * 2, 3)
    printer(line, 3)

def print_command_help(command):
    printer("Usage:", 2)
    printer(command.get_usage())
    printer("")
    printer("Options:", 2)

    options = command.get_options()
    options.sort(cmp=lambda x,y: cmp(x['name'], y['name']))
    options = options + [{'name': '--help', 'description': 'Display help message'}]

    longest_option = 0
    for option in options:
        longest_option = max(longest_option, len(option['name']))

    for option in options:
        nb_spaces = longest_option + 2 - len(option['name'])
        printer("  " + get_color(1) + option['name'] + get_color() + (' ' * nb_spaces) + option['description'])

    printer("")
    printer("Help:", 2)
    printer("  " + command.get_description())


def make_request(endpoint, type=None, configuration=None):
    url = base_url + endpoint

    if type == 'POST':
        return requests.post(url, auth=(username, password), data={'configuration': json.dumps(configuration, separators=(',', ': '))})

    if type == 'DELETE':
        return requests.delete(url, auth=(username, password))

    if type == 'PUT':
        return requests.put(url, auth=(username, password), data={'configuration': json.dumps(configuration, separators=(',', ': '))})

    r = requests.get(url, auth=(username, password))

    return r.text


def get_configs_from_website():
    live_connectors = json.loads(make_request('/'))['connectors']
    live_connectors.sort(key=lambda x: x['name'])

    configs = {}
    inverted = {}
    for connector in live_connectors:
        configs[connector['name']] = connector['configuration']
        inverted[connector['name']] = connector['id']

    return configs, inverted
