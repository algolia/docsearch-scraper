import os
from algoliasearch import algoliasearch

app_id = os.environ['APPLICATION_ID'] if 'APPLICATION_ID' in os.environ else ''
api_key = os.environ['API_KEY'] if 'API_KEY' in os.environ else ''

algolia_client = algoliasearch.Client(app_id, api_key)


def get_facets(config):
    index = algolia_client.init_index(config)

    try:
        res = index.search('', {
            'facets': '*',
            'maxValuesPerFacet': 1000,
            'hitsPerPage': 0
        })
    except Exception:
        return None

    if 'facets' in res:
        return res['facets']

    return None


def update_docsearch_key(config, key):
    index = algolia_client.init_index(config)

    index.update_user_key(key, {
        'indices': [config],
        'description': 'docsearch frontend ' + config,
        'acl': ['search']
    })


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
        'description': 'docsearch frontend ' + config,
        'acl': ['search']
    })

    return response['key']


def delete_docsearch_key(config):
    index = algolia_client.init_index(config)

    for key in index.list_user_keys()['keys']:
        if 'description' in key and 'docsearch frontend' in key['description']:
            index.delete_user_key(key['value'])


def delete_docsearch_index(config):
    algolia_client.delete_index(config)
