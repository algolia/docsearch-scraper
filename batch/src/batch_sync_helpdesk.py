"""
Script that sync conversation ID to the missing file
"""
from deployer.src import helpdesk_helper
import os
import sys
import json
from collections import OrderedDict
from deployer.src import algolia_helper


def batch_sync_helpdesk(args):

    if 'APPLICATION_ID' not in os.environ or 'API_KEY' not in os.environ:
        print("")
        print("ERROR: missing configuration")
        print("")
        sys.exit(1)

    print("Please git pull before to batch")

    configs_to_process = pick_configs(is_missing_conversation_id)

    unfound_conf=[]

    for position, conf in enumerate(configs_to_process):

        if position < 10:
            docsearch_key = algolia_helper.get_docsearch_key(conf["index_name"]).__str__()
            search_results = helpdesk_helper.search("body:{} AND mailbox:\"Algolia DocSearch\"".format(docsearch_key))

            if search_results.get("count") == 1:

                processed_conf = process_when_success(search_results, conf)
                write_outcome("outcome/{}.json".format(conf["index_name"]),processed_conf)


            elif search_results.get("count") == 0:

                search_results = helpdesk_helper.search(
                    "body:{} AND mailbox:\"Algolia DocSearch\"".format(conf["index_name"]))

                if search_results.get("count") == 0:
                    unfound_conf.append(conf["index_name"])
                elif search_results.get("count") == 1:
                    processed_conf = process_when_success(search_results, conf)
                    write_outcome("outcome/{}.json".format(conf["index_name"]), processed_conf)
                else:
                    process_when_many_results(search_results, conf)
            else:
                process_when_many_results(search_results, conf)

    if len(unfound_conf):
        for conf in unfound_conf:
            print conf

def pick_configs(filter_conf):
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
                if filter_conf != None and filter_conf(config):
                    configs.append(config)
                else:
                    configs.append(config)

    return configs

def is_missing_conversation_id(config):
    '''
    :param config: JSON object
    :return: True if the config miss the conversation ID 
    '''
    
    return not "conversation_id" in config

def write_outcome(path, data=None):

    if data == None:
        print "Nothing to write"
        return -1

    try:
        with open(path, 'w') as f:
            f.write(data)
    except IOError:
        print "couldn't write {}".format(path)
        raise

def process_when_success(search_results, conf):

    conv_id = search_results.get("items")[0].get("id")
    conf["conversation_id"] = [conv_id]
    return json.dumps(conf,
                      separators=(',', ': '),
                      indent=2,
                      ensure_ascii=False)

def process_when_many_results(search_results, conf):

    print ""
    print conf["index_name"]
    for conv in search_results.get("items"):
        print helpdesk_helper.get_conversation_url_from_cuid(conv.get("id").__str__())
    print ""