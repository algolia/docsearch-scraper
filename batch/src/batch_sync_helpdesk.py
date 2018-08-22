"""
Script that sync conversation ID to the missing file
"""
from deployer.src import helpdesk_helper
import os
import sys
import json
from collections import OrderedDict
from deployer.src import algolia_helper, helpers


def batch_sync_helpdesk(args):
    if 'APPLICATION_ID' not in os.environ or 'API_KEY' not in os.environ:
        print("")
        print("ERROR: missing configuration")
        print("")
        sys.exit(1)

    print("Please git pull before to batch")

    configs_to_process = pick_configs(is_missing_conversation_id)

    unfound_conf = []

    for position, conf in enumerate(configs_to_process):
        docsearch_key = algolia_helper.get_docsearch_key(conf["index_name"]).__str__()
        search_results = helpdesk_helper.search("body:{} AND mailbox:\"Algolia DocSearch\"".format(docsearch_key))
        if search_results.get("count") == 1:

            process_and_write_conf(search_results, conf, process_when_success)

        elif search_results.get("count") == 0:

            search_results = helpdesk_helper.search(
                "body:{} AND mailbox:\"Algolia DocSearch\"".format(conf["index_name"]))

            if search_results.get("count") == 0:
                unfound_conf.append(conf["index_name"])
            elif search_results.get("count") == 1:
                process_and_write_conf(search_results, conf, process_when_success)
            else:
                process_and_write_conf(search_results, conf, process_when_many_results)
        else:
            process_and_write_conf(search_results, conf, process_when_many_results)

    if len(unfound_conf):
        for conf in unfound_conf:
            print(conf)


def pick_configs(filter_conf):
    configs = []

    base_dir = os.path.dirname(__file__)

    for dir in ['public/configs']:
        base_dir = base_dir + '/../../configs/' + dir
        for f in os.listdir(base_dir):
            path = base_dir + '/' + f

            if 'json' not in path:
                continue

            if os.path.isfile(path):
                with open(path, 'r') as f:
                    txt = f.read()
                config = json.loads(txt, object_pairs_hook=OrderedDict)
                if filter_conf is not None and filter_conf(config):
                    configs.append(config)
                else:
                    configs.append(config)

    return configs


def is_missing_conversation_id(config):
    """"
    :param config: JSON object
    :return: True if the config miss the conversation ID 
    """

    return "conversation_id" not in config


def process_when_success(search_results, conf):
    cuid = search_results.get("items")[0].get("id")
    return update_conf_with_cuid(conf, cuid)


def update_conf_with_cuid(conf, cuid):
    conf["conversation_id"] = [cuid.__str__()]

    conf = OrderedDict(sorted(conf.items(),
                              key=key_sort)
                       )

    return json.dumps(conf,
                      separators=(',', ': '),
                      indent=2)


def key_sort(attr):
    ref = {
        "index_name": 0,
        "start_urls": 1,
        "sitemap_urls": 2,
        "sitemap_urls_regexs": 3,
        "stop_urls": 4,
        "force_sitemap_urls_crawling": 5,
        "strict_redirects": 6,
        "selectors": 7,
        "selectors_exclude": 8,
        "stop_content": 9,
        "strip_chars": 10,
        "keep_tags": 11,
        "min_indexed_level": 12,
        "only_content_level": 13,
        "js_render": 14,
        "js_wait": 15,
        "use_anchors": 16,
        "custom_settings": 17,
        "synonyms": 18,
        "docker_memory": 19,
        "docker_cpu": 20,
        "conversation_id": 28,
        "comments": 29,
        "nb_hits": 30
    }
    if attr[0] in ref.keys():
        return ref[attr[0]]
    else:
        return 27


def process_when_many_results(search_results, conf):
    print("\n" + conf["index_name"])
    for conv in search_results.get("items"):
        print helpdesk_helper.get_conversation_url_from_cuid(conv.get("id").__str__())

    return update_conf_with_cuid(conf, helpers.get_user_value("Right conversation ID\n"))


def write_outcome(path, data=None):
    if data is None:
        print "Nothing to write"
        return -1

    try:
        with open(path, 'w') as f:
            f.write(data)
    except IOError:
        print "couldn't write {}".format(path)
        raise


def process_and_write_conf(search_results,
                           conf,
                           process_conf_and_results):
    write_outcome(
        "outcome/{}.json".format(
            conf["index_name"]),
        process_conf_and_results(search_results, conf)
    )
