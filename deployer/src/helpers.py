import requests
import json
import os

username = os.environ['WEBSITE_USERNAME'] if 'WEBSITE_USERNAME' in os.environ else ''
password = os.environ['WEBSITE_PASSWORD'] if 'WEBSITE_PASSWORD' in os.environ else ''

base_url = 'https://www.algolia.com/api/1/docsearch'


def confirm(message="Confirm"):
    prompt = message + ' [y/n]:\n'

    while True:
        ans = raw_input(prompt)
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def get_user_value(message):
    prompt = message
    return raw_input(prompt)


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
