from collections import OrderedDict
import tldextract
from . import helpers
from . import helpdesk_helper


def to_docusaurus_config(config):
    config["selectors"]["lvl0"] = OrderedDict((
        ("selector", "//*[contains(@class,'navGroupActive')]//a[contains(@class,'navItemActive')]/preceding::h3[1]"),
        ("type", "xpath"),
        ("global", True),
        ("default_value", "Documentation")
    ))
    config["selectors"]["lvl1"] = ".post h1"
    config["selectors"]["lvl2"] = ".post h2"
    config["selectors"]["lvl3"] = ".post h3"
    config["selectors"]["lvl4"] = ".post h4"
    config["selectors"]["text"] = ".post article p, .post article li"
    config["selectors_exclude"] = [".hash-link"]

    return config


def to_gitbook_config(config):

    config["selectors"]["lvl0"] = ".markdown-section h1"
    config["selectors"]["lvl1"] = ".markdown-section h2"
    config["selectors"]["lvl2"] = ".markdown-section h3"
    config["selectors"]["lvl3"] = ".markdown-section h4"
    config["selectors"]["lvl4"] = ".markdown-section h4"
    config["selectors"]["text"] = ".markdown-section p, .markdown-section li"

    return config


def to_pkgdown_config(config, urls=None):

    start_url = None

    if urls:
        start_url = urls[0]

    config["selectors"]["lvl0"] = OrderedDict((
            ("selector", ".contents h1"),
            ("default_value", "Documentation")
        ))
    config["selectors"]["lvl1"] = ".contents h2"
    config["selectors"]["lvl2"] = ".contents h3, .contents th"
    config["selectors"]["lvl3"] = ".contents h4"
    config["selectors"]["lvl4"] = ".contents h5"
    config["selectors"]["text"] = ".contents p, .contents li, .usage, .template-article .contents .pre"
    config["selectors_exclude"] = [".dont-index"]
    config["sitemap_urls"] = [start_url + "sitemap.xml"]
    config["custom_settings"] = {"separatorsToIndex": "_"}
    # config["stop_urls"] = [start_url + "index.html", "LICENSE-text.html"]
    config["sitemap_urls"] = [start_url + "sitemap.xml"]
    return config


def create_config(u=None):
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

    if u is None:
        u = helpers.get_user_value("start url: ")

    urls = [u]

    if helpdesk_helper.is_helpdesk_url(u):
        cuid = helpdesk_helper.get_conversation_ID_from_url(u)

        conversation = helpdesk_helper.get_conversation(cuid)
        url_from_conversation = helpdesk_helper.get_start_url_from_conversation(conversation)
        urls = [url_from_conversation]
        u = url_from_conversation

        if helpdesk_helper.is_docusaurus_conversation(conversation):
            config = to_docusaurus_config(config)
        elif helpdesk_helper.is_gitbook_conversation(conversation):
            config = to_gitbook_config(config)
        elif helpdesk_helper.is_pkgdown_conversation(conversation):
            config = to_pkgdown_config(config, urls)

        config["conversation_id"] = [cuid]

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

    user_index_name = helpers.get_user_value(
        "index_name is " + "\033[1;33m" + config['index_name'] + "\033[0m" + ' [enter to confirm]: ')

    if user_index_name != "":
        config['index_name'] = user_index_name
        print("index_name is now " + "\033[1;33m" + config['index_name'] + "\033[0m")

    return config
