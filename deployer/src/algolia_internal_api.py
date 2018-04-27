import requests
from os import environ
from base64 import b64encode


def get_endpoint(endpoint, params=''):
    base_endpoint = environ.get('BASE_INTERNAL_ENDPOINT')

    return base_endpoint + endpoint + params


def get_headers():
    token = environ.get('INTERNAL_API_AUTH')

    app_id = environ.get('APPLICATION_ID_PROD')
    admin_api_key = environ.get('API_KEY_PROD')
    auth_token = b64encode(app_id + ":" + admin_api_key).replace('=', '').replace("\n", '')

    return {
        'Authorization': 'Basic ' + token,
        'Algolia-Application-Authorization': 'Basic ' + auth_token
    }


def get_application_rights():
    app_id = environ.get('APPLICATION_ID_PROD')
    endpoint = get_endpoint('/applications/' + app_id)#, '?fields=application_rights')

    r = requests.get(endpoint, headers=get_headers())

    data = r.json()

    return data['application_rights']


def get_right_for_email(email):
    rights = get_application_rights()

    for right in rights:
        if right['user']['email'] == email:
            return right


def get_indices_for_right(right):
    if right is not None:
        return right['indices']
    return []


def add_user_to_index(config, email):
    right = get_right_for_email(email)
    indices = get_indices_for_right(right)

    if config in indices:
        return

    indices.append(config)

    if right:
        requests.patch(get_endpoint('/application_rights/' + str(right['id'])), json={
            'application_right': {
                'application_id': 13240,  # website internal docsearch app id
                'user_email': email,
                'indices': indices,
                'analytics': True
            }
        }, headers=get_headers())
    else:
        requests.post(get_endpoint('/application_rights'), json={
            'application_right': {
                'application_id': 13240, # website internal docsearch app id
                'user_email': email,
                'indices': indices,
                'analytics': True
            }
        }, headers=get_headers())

def remove_user_from_index(config, email):
    right = get_right_for_email(email)
    indices = get_indices_for_right(right)

    if config in indices:
        indices.remove(config)

    if len(indices) > 0:
        requests.patch(get_endpoint('/application_rights/' + str(right['id'])), json={
            'application_right': {
                'application_id': 13240,  # website internal docsearch app id
                'user_email': email,
                'indices': indices,
                'analytics': True
            }
        }, headers=get_headers())
    else:
        requests.delete(get_endpoint('/application_rights/' + str(right['id'])), headers=get_headers())

