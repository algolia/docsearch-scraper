import os
import json
from collections import OrderedDict

import helpers

def get_configs_from_repos():
    configs = {}

    base_dir = os.path.dirname(__file__)

    for dir in ['public', 'private']:
        dir = base_dir + '/../' + dir
        for f in os.listdir(dir):
            path = dir + '/' + f

            if 'json' not in path:
                continue

            if os.path.isfile(path):
                with open(path, 'r') as f:
                    txt = f.read()
                config = json.loads(txt, object_pairs_hook=OrderedDict)
                configs[config['index_name']] = config

    print str(len(configs)) + " docs in public and private repo"

    return configs


def get_configs_from_website():
    live_connectors = json.loads(helpers.make_request('/'))['connectors']
    live_connectors.sort(key=lambda x: x['name'])

    configs = {}
    inverted = {}
    for connector in live_connectors:
        configs[connector['name']] = connector['configuration']
        inverted[connector['name']] = connector['id']

    print str(len(configs)) + " docs in website connectors"

    return configs, inverted