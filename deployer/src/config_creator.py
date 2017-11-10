from collections import OrderedDict
import json
import tldextract
import pyperclip
import re
from . import helpers
from .html_helper import get_main_selector
import json


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_conversation_ID_from_url(hs_url):
    capture_conversation_uid = re.compile('.+/conversation/(\d+)/.*')
    cuid = capture_conversation_uid.match(hs_url).group(1)

    if not len(cuid) > 0:
        raise ValueError("Wrong help scout url " + hs_url + ", must have a conversation sub part with ID")

    if not RepresentsInt(cuid):
        raise ValueError("Conversation ID : " + cuid + " must be an integer")

    return cuid

def get_conversation(cuid):

    conversation_endpoint = "https://api.helpscout.net/v1/conversations/" + cuid + ".json"
    hs_api_key=helpers.getHelpScoutAPIKey()

    response_json = json.loads(helpers.make_request(conversation_endpoint, username=hs_api_key, password="X"))
    conversation = response_json.get('item')

    if not conversation:
        raise ValueError("Wrong json returned from help scout, must have an item attribute")

    return conversation

def get_start_url_from_conversation(conversation):

    # The message to extract is the first from the thread and it was sent by a customer
    first_thread = conversation.get('threads')[-1]
    was_sent_by_customer = first_thread.get('createdByCustomer')
    url_from_conversation = first_thread.get('body')

    if not len(url_from_conversation):
        raise ValueError("First thread from the conversation thread is empty")

    if not was_sent_by_customer:
        raise ValueError("First thread from the conversation thread wasn't sent by customer")

    print "URL fetched is \033[1;36m" + url_from_conversation + "\033[0m sent by \033[1;33m" + first_thread.get("customer").get("email") + "\033[0m"

    return url_from_conversation


def create_config():
    config = OrderedDict((
        ("index_name", ""),
        ("start_urls", []),
        ("stop_urls", []),
        ("selectors", OrderedDict((
            ("lvl0", "FIXME h1"),
            ("lvl1", "FIXME h2"),
            ("lvl2", "FIXME h3"),
            ("lvl3", "FIXME h4"),
            ("lvl4", "FIXME h5"),
            ("text", "FIXME p, FIXME li")
        )))
    ))

    u = helpers.get_user_value("start url: ")
    urls = [u]

    if 'secure.helpscout.net/conversation' in u:
        cuid = get_conversation_ID_from_url(u)

        conversation = get_conversation(cuid)
        url_from_conversation = get_start_url_from_conversation(conversation)

        config["conversation_id"] = [cuid]

        urls = [url_from_conversation]
        u = url_from_conversation

    if '.html' in u:
        urls.append(u.rsplit('/', 1)[0])

    config['index_name'] = tldextract.extract(u).domain

    if helpers.confirm("Does the start_urls require variables ?"):
        config['start_urls'] = [{
            "url": u + ('/' if u[-1] != '/' else '') + '(?P<static_variable>.*?)/(?P<dynamic_variable>.*?)/',
            "variables": {
                "static_variable": [
                    "value1",
                    "value2"
                ],
                "dynamic_variable": {
                    "url": u,
                    "js": "var versions = $('#selector option').map(function (i, elt) { return $(elt).html(); }).toArray(); return JSON.stringify(versions);"
                }
            }
        }]

    else:
        config['start_urls'] = urls

    main_selector = get_main_selector(u)

    if main_selector is not None:
        for selector in config['selectors']:
            config['selectors'][selector] = config['selectors'][selector].replace('FIXME', main_selector)

    dump = json.dumps(config, separators=(',', ': '), indent=2)
    pyperclip.copy(dump)

    print("")
    print("=============")
    print(dump)
    print("=============")
    print("")
    print("Config copied to clipboard [OK]")
    print("")
