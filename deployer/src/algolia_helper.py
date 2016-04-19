from algoliasearch import algoliasearch
import os

app_id = os.environ['APP_ID']
api_key = os.environ['API_KEY']

algolia_client = algoliasearch.Client(app_id, api_key)

def get_docsearch_key(config):
    index = algolia_client.init_index(config)
    k = 'Not found'
    # find a key
    for key in index.list_user_keys()['keys']:
        if 'description' in key and 'docsearch frontend' in key['description']:
            k = key['value']

    return k

def add_docsearch_key(config):
    index = algolia_client.init_index(config)

    response = index.add_user_key({
        'indices': [config],
        'description': 'docsearch frontend ' + config
    })

    return response['key']

def delete_docsearch_key(config):
    index = algolia_client.init_index(config)

    for key in index.list_user_keys()['keys']:
        if 'description' in key and 'docsearch frontend' in key['description']:
            index.delete_user_key(key['value'])

def delete_docsearch_index(config):
    algolia_client.delete_index(config)
