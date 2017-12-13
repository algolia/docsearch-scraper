from collections import OrderedDict
import tldextract
import pyperclip
from . import helpers
from .html_helper import get_main_selector
import json
from . import helpdesk_helper

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

    if  helpdesk_helper.is_helpdesk_url(u):
        cuid = helpdesk_helper.get_conversation_ID_from_url(u)

        conversation = helpdesk_helper.get_conversation(cuid)
        url_from_conversation = helpdesk_helper.get_start_url_from_conversation(conversation)

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
