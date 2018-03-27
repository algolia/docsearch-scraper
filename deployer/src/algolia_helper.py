import os
from algoliasearch import algoliasearch

app_id = os.environ['APPLICATION_ID'] if 'APPLICATION_ID' in os.environ else ''
api_key = os.environ['API_KEY'] if 'API_KEY' in os.environ else ''

app_id_prod = os.environ['APPLICATION_ID_PROD'] if 'APPLICATION_ID_PROD' in os.environ else ''
api_key_prod = os.environ['API_KEY_PROD'] if 'API_KEY_PROD' in os.environ else ''

algolia_client = algoliasearch.Client(app_id, api_key)
algolia_client_prod = algoliasearch.Client(app_id_prod, api_key_prod)


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

def remove_crawling_issue(config):
    app_id = os.environ['APPLICATION_ID_PROD'] if 'APPLICATION_ID_PROD' in os.environ else ''
    api_key = os.environ['API_KEY_PROD'] if 'API_KEY_PROD' in os.environ else ''

    client = algoliasearch.Client(app_id, api_key)
    index = client.init_index(config)

    index.set_settings({
        'userData': {
            'crawling_issue': False
        }
    })


def update_docsearch_key(config, key):
    algolia_client_prod.update_api_key()(key, {
        'indices': [config],
        'description': 'docsearch frontend ' + config,
        'acl': ['search']
    })


def get_docsearch_key(config):
    k = 'Not found'
    # find a key
    for key in algolia_client_prod.list_api_keys()['keys']:
        if 'description' in key and 'docsearch frontend ' + config == key['description'] and key["acl"]==["search"]:
            k = key['value']
    return k


def add_docsearch_key(config):
    if not isinstance(config, unicode) or '*' in config:
        raise ValueError("index name : {} is not safe".format(config))

    response = algolia_client_prod.add_api_key({
        'indices': [config],
        'description': 'docsearch frontend ' + config,
        'acl': ['search']
    })

    return response['key']


def delete_docsearch_key(config):
    key_to_delete = get_docsearch_key(config)
    algolia_client_prod.delete_api_key(key_to_delete)


def delete_docsearch_index(config):
    algolia_client_prod.delete_index(config)
