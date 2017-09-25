import os

username = os.environ['WEBSITE_USERNAME'] if 'WEBSITE_USERNAME' in os.environ else ''
password = os.environ['WEBSITE_PASSWORD'] if 'WEBSITE_PASSWORD' in os.environ else ''

slack_hook = os.environ['SLACK_HOOK'] if 'SLACK_HOOK' in os.environ else ''

base_url = 'https://www.algolia.com/api/1/docsearch'


def confirm(message="Confirm"):
    from builtins import input

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


def get_user_value(message):
    from builtins import input

    prompt = message
    return input(prompt)


def make_custom_get_request(url):
    import requests

    return requests.get(url)


def make_request(endpoint, type=None, configuration=None):
    import requests
    import json

    url = base_url + endpoint

    success_codes = [200, 201, 204]

    if type == 'POST':
        r = requests.post(url, auth=(username, password), data={'configuration': json.dumps(configuration, separators=(',', ': '))})

        if r.status_code / 100 != 2:
            print("ISSUE for POST request : " + url + " with params: " + json.dumps(configuration, separators=(',', ': ')))
        return r

    if type == 'DELETE':
        r = requests.delete(url, auth=(username, password))

        if r.status_code not in success_codes:
            print("ISSUE for DELETE request : " + url + " with params: " + json.dumps(configuration, separators=(',', ': ')))
        return r

    if type == 'PUT':
        r = requests.put(url, auth=(username, password), data={'configuration': json.dumps(configuration, separators=(',', ': '))})
        print(r.status_code)
        if r.status_code / 100 != 2:
            print("ISSUE for PUT request : " + url + " with params: " + json.dumps(configuration, separators=(',', ': ')))
        return r

    r = requests.get(url, auth=(username, password))

    if r.status_code / 100 != 2:
        print("ISSUE for GET request : " + url + " with params: None")

    return r.text


def send_slack_notif(reports):
    if slack_hook == '':
        print('NO SLACK_HOOK')

    from slacker import Slacker

    slack = Slacker(None, slack_hook)

    slack.incomingwebhook.post({
        "text": "",
        "channel": "#notif-docsearch",
        "username": "Deployer",
        "icon_emoji": ":rocket:",
        "attachments": reports
    })