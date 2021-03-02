import os
from algoliasearch.search_client import SearchClient

app_id = os.environ.get('APPLICATION_ID', '')

api_key = os.environ.get('API_KEY', '')

app_id_prod = os.environ.get('APPLICATION_ID_PROD', '')
api_key_prod = os.environ.get('API_KEY_PROD', '')

algolia_client = SearchClient.create(app_id, api_key)
algolia_client_prod = SearchClient.create(app_id_prod, api_key_prod)


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
    algolia_client_prod.update_api_key(key, {
        'indexes': [config],
        'description': 'docsearch frontend ' + config,
        'acl': ['search']
    })


def get_docsearch_key(config):
    k = 'Not found'
    # find a key
    for key in algolia_client_prod.list_api_keys()['keys']:
        if 'description' in key and 'docsearch frontend ' + config == key['description'] and key["acl"] == ["search"]:
            k = key['value']
    return k


def add_docsearch_key(config):
    if not isinstance(config, str) or '*' in config:
        raise ValueError("index name : {} is not safe".format(config))

    response = algolia_client_prod.add_api_key(['search'], {
        'indexes': [config],
        'description': 'docsearch frontend ' + config,
    })

    return response['key']


def delete_docsearch_key(config):
    key_to_delete = get_docsearch_key(config)
    algolia_client_prod.delete_api_key(key_to_delete)


def delete_docsearch_index(config):
    algolia_index = algolia_client_prod.init_index(config)
    algolia_index.delete()


def list_index_analytics_key(config_name):
    analytics_keys = []
    keys = algolia_client_prod.list_api_keys()['keys']
    for key in keys:
        if 'indexes' in key and config_name in key['indexes'] and 'analytics' in key['acl']:
            analytics_keys.append(key)
    return analytics_keys
