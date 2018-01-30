from collections import OrderedDict
import tldextract
import pyperclip
from . import helpers
from .html_helper import get_main_selector
import json
from . import helpdesk_helper

def to_docusaurus_config(config):

    config["selectors"]["lvl0"]=OrderedDict((
            ("selector", "//*[contains(@class,'navGroupActive')]//a[contains(@class,'navItemActive')]/preceding::h3[1]"),
            ("type", "xpath"),
            ("global", True),
            ("default_value", "Documentation")
        ))
    config["selectors"]["lvl1"]=".post h1"
    config["selectors"]["lvl2"]=".post h2"
    config["selectors"]["lvl3"]=".post h3"
    config["selectors"]["lvl4"]=".post h4"
    config["selectors"]["text"]=".post article p, .post article li"
    config["selectors_exclude"]=[".hash-link"]

    return config

def create_config( u = None):
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

    if u == None :
        u = helpers.get_user_value("start url: ")

    urls = [u]

    if  helpdesk_helper.is_helpdesk_url(u):
        cuid = helpdesk_helper.get_conversation_ID_from_url(u)

        conversation = helpdesk_helper.get_conversation(cuid)
        url_from_conversation = helpdesk_helper.get_start_url_from_conversation(conversation)

        if helpdesk_helper.is_docusaurus_conversation(conversation):
            config = to_docusaurus_config(config)

        config["conversation_id"] = [cuid]

        urls = [url_from_conversation]
        u = url_from_conversation

    if '.html' in u:
        urls.append(u.rsplit('/', 1)[0])

    # Use subdomain for github website https://<subdomain>.github.io/
    config['index_name'] = tldextract.extract(u).subdomain if tldextract.extract(u).domain == 'github' else tldextract.extract(u).domain

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

    dump = json.dumps(config, separators=(',', ': '), indent=2)
    pyperclip.copy(dump)

    print("")
    print("=============")
    print(dump)
    print("=============")
    print("")
    print("Config copied to clipboard [OK]")
    print("")
