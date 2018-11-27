import os

USERNAME = os.environ.get('WEBSITE_USERNAME', '')
PASSWORD = os.environ.get('WEBSITE_PASSWORD', '')

api_key_prod = os.environ.get('API_KEY_PROD', '')

slack_hook = os.environ.get('SLACK_HOOK', '')

base_url = os.environ.get('ALGOLIA_DOCSEARCH_API', None)


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


def make_request(endpoint, type=None, data=None, username=None, password=None,
                 json_request=False):
    import requests

    url = base_url + endpoint if "://" not in endpoint else endpoint

    success_codes = [200, 201, 204]

    username = username if username else USERNAME
    password = password if password else PASSWORD

    if data and not isinstance(data, dict):
        raise ValueError(data + " must be a dict ")

    if type == 'POST':
        if json_request:
            r = requests.post(url,
                              auth=(username, password),
                              json=data)
        else:
            r = requests.post(url,
                              auth=(username, password),
                              data=data)

        if r.status_code / 100 != 2:
            print("ISSUE for POST request : " + url + " with params: " + str(
                data))
            print(r.text)
        return r

    if type == 'DELETE':
        r = requests.delete(url,
                            auth=(username, password))

        if r.status_code not in success_codes:
            print("ISSUE for DELETE request : " + url + " with params: " + str(
                data))
        return r

    if type == 'PUT':
        r = requests.put(url,
                         auth=(username, password),
                         data=data)
        print(r.status_code)
        if r.status_code / 100 != 2:
            print("ISSUE for PUT request : " + url + " with params: " + str(
                data))
        return r

    if data != None:
        r = requests.get(url,
                         auth=(username, password),
                         params=data)
    else:
        r = requests.get(url,
                         auth=(username, password))

    if r.status_code / 100 != 2:
        print("ISSUE for GET request : " + url + " with params:" + data)

    if json_request:
        r.json()

    return r.text


def send_slack_notif(reports):
    if slack_hook == '':
        raise ValueError("NO SLACK_HOOK")

    from slacker import Slacker

    slack = Slacker(None, slack_hook)

    slack.incomingwebhook.post({
        "text": "",
        "channel": "#notif-docsearch",
        "username": "Deployer",
        "icon_emoji": ":rocket:",
        "attachments": reports
    })
