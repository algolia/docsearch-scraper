"""
Script that sync conversation ID to the missing file
"""
from deployer.src import helpdesk_helper
import os
import sys
import json
from collections import OrderedDict
from deployer.src import algolia_helper


def sync_helpdesk(args):

    if 'APPLICATION_ID' not in os.environ or 'API_KEY' not in os.environ:
        print("")
        print("ERROR: missing configuration")
        print("")
        sys.exit(1)

    print("sync_helpdesk")
    configs_to_process = get_configs_with_no_cuid()
    for position, conf in enumerate(configs_to_process):

        docsearch_key = algolia_helper.get_docsearch_key(conf["index_name"]).__str__()

        search_results = helpdesk_helper.search("body:{} AND mailbox:\"Algolia DocSearch\"".format(docsearch_key))

        if(search_results.get("count") == 1):
            conv_id = search_results.get("items")[0].get("id")
            conf["conversation_id"] = [conv_id]
            dump = json.dumps(conf,
                              separators=(',', ': '),
                              indent=2,
                              ensure_ascii=False)

            with open("{}.json".format(conf["index_name"]), 'w') as f:
                f.write(dump)
        else:
            print search_results

def get_configs_with_no_cuid():
    configs = []

    base_dir = os.path.dirname(__file__)

    for dir in ['public/configs']:
        dir = base_dir + '/../../configs/' + dir
        for f in os.listdir(dir):
            path = dir + '/' + f

            if 'json' not in path:
                continue

            if os.path.isfile(path):
                with open(path, 'r') as f:
                    txt = f.read()
                config = json.loads(txt, object_pairs_hook=OrderedDict)
                if not "conversation_id" in config:
                    configs.append(config)
    return configs