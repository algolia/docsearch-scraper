import os
import json
from collections import OrderedDict
from os import environ


def get_configs_from_repos():
    configs = {}
    public_dir = environ.get('PUBLIC_CONFIG_FOLDER')
    private_dir = environ.get('PRIVATE_CONFIG_FOLDER')

    if public_dir is None or private_dir is None:
        print(
            'PUBLIC_CONFIG_FOLDER and PRIVATE_CONFIG_FOLDER must be defined in the environment')
        exit()

    for dir in [public_dir + '/configs', private_dir + '/configs']:
        for f in os.listdir(dir):
            path = dir + '/' + f

            if 'json' not in path:
                continue

            if os.path.isfile(path):
                with open(path, 'r') as f:
                    txt = f.read()
                config = json.loads(txt, object_pairs_hook=OrderedDict)
                configs[config['index_name']] = config
    print('{} docs in public and private repo'.format(len(configs)))

    return configs
