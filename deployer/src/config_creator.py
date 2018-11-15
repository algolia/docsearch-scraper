from collections import OrderedDict
import tldextract
import re
from . import helpers
from . import helpdesk_helper
from urlparse import urlparse


def extract_root_from_input(input_string):
    # We cant parse the url since user might have not enter a proper link

    # We assume that the string is already the proper root
    if input_string.endswith('/'):
        return input_string
    # extracting substring before the first isolated / (not //)
    domain = re.match(".+?([^\/]\/(?!\/))",
                      input_string)
    try:
        url_parsed = urlparse(input_string);
        # Removing unused parameters
        url_parsed._replace(params='', query='', fragment='')
        path_splited = url_parsed.path.split('/')

        # Path is redirecting to a page
        if ('html' in path_splited[-1]):
            url_parsed = url_parsed._replace(path='/'.join(path_splited[: -1]))
        # We are fine
        else:
            pass

        return url_parsed.geturl()
    except ValueError:
        return domain.group() if domain else input_string


def to_docusaurus_config(config, urls=None):
    if urls:
        config["sitemap_urls"] = [
            extract_root_from_input(urls[0]) + "sitemap.xml"]
        config["sitemap_alternate_links"] = True
        config["custom_settings"] = {"attributesForFaceting": ["language",
                                                               "version"]
                                     }

    config["selectors"]["lvl0"] = OrderedDict((
        ("selector",
         "//*[contains(@class,'navGroups')]//*[contains(@class,'navListItemActive')]/preceding::h3[1]"),
        ("type", "xpath"),
        ("global", True),
        ("default_value", "Documentation")
    ))
    config["selectors"]["lvl1"] = ".post h1"
    config["selectors"]["lvl2"] = ".post h2"
    config["selectors"]["lvl3"] = ".post h3"
    config["selectors"]["lvl4"] = ".post h4"
    config["selectors"]["lvl5"] = ".post h5"
    config["selectors"]["text"] = ".post article p, .post article li"
    config["selectors_exclude"] = [".hash-link"]

    return config


def to_gitbook_config(config):
    config["selectors"]["lvl0"] = ".markdown-section h1"
    config["selectors"]["lvl1"] = ".markdown-section h2"
    config["selectors"]["lvl2"] = ".markdown-section h3"
    config["selectors"]["lvl3"] = ".markdown-section h4"
    config["selectors"]["lvl4"] = ".markdown-section h4"
    config["selectors"]["lvl5"] = ".markdown-section h5"
    config["selectors"]["text"] = ".markdown-section p, .markdown-section li"

    return config


def to_pkgdown_config(config, urls=None):
    if urls:
        config["sitemap_urls"] = [
            extract_root_from_input(urls[0]) + "sitemap.xml"]

    config["selectors"]["lvl0"] = OrderedDict((
        ("selector", ".contents h1"),
        ("default_value", "Documentation")
    ))
    config["selectors"]["lvl1"] = ".contents h2"
    config["selectors"]["lvl2"] = ".contents h3, .contents th"
    config["selectors"]["lvl3"] = ".contents h4"
    config["selectors"]["lvl4"] = ".contents h5"
    config["selectors"][
        "text"] = ".contents p, .contents li, .usage, .template-article .contents .pre"
    config["selectors_exclude"] = [".dont-index"]
    config["custom_settings"] = {"separatorsToIndex": "_"}
    config["scrap_start_urls"] = False
    config["stop_urls"] = ["LICENSE-text.html"]
    return config


def to_vuepress_config(config):
    config["selectors"]["lvl0"] = OrderedDict((
        ("selector", "p.sidebar-heading.open"),
        ("global", True),
        ("default_value", "Documentation")
    ))
    config["custom_settings"] = {"attributesForFaceting": ["lang"]
                                 }
    config["selectors"]["lvl1"] = ".content h1"
    config["selectors"]["lvl2"] = ".content h2"
    config["selectors"]["lvl3"] = ".content h3"
    config["selectors"]["lvl4"] = ".content h4"
    config["selectors"]["lvl5"] = ".content h5"
    config["selectors"]["text"] = ".content p, .content li"
    config["selectors"]["lang"] = OrderedDict((
        ("selector", "/html/@lang"),
        ("type", "xpath"),
        ("global", True),
        ("default_value", "en-US")
    ))

    config["scrap_start_urls"] = False
    config["strip_chars"] = " .,;:#"

    return config


def to_larecipe_config(config, urls=None):
    if urls:
        config["sitemap_urls"] = [
            extract_root_from_input(urls[0]) + "sitemap.xml"]
    config["selectors"]["lvl0"] = OrderedDict((
        ("selector",
         "//div[contains(@class, 'sidebar')]//li/a[text()=//div[contains(@class, 'article')]//h1[1]/text()]"),
        ("global", True),
        ("type", "xpath"),
        ("default_value", "Documentation")
    ))

    config["selectors"]["lvl1"] = "div.article h1"
    config["selectors"]["lvl2"] = "div.article h2"
    config["selectors"]["lvl3"] = "div.article h3"
    config["selectors"]["lvl4"] = "div.article h4"
    config["selectors"]["lvl5"] = "div.article h5"
    config["selectors"]["text"] = "div.article p, div.article li"

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
            ("lvl5", "FIXME h6"),
            ("text", "FIXME p, FIXME li")
        )))
    ))

    if u is None:
        u = helpers.get_user_value("start url: ")

    urls = [u]

    if helpdesk_helper.is_helpdesk_url(u):
        cuid = helpdesk_helper.get_conversation_ID_from_url(u)

        conversation = helpdesk_helper.get_conversation(cuid)
        url_from_conversation = helpdesk_helper.get_start_url_from_conversation(
            conversation)
        urls = [url_from_conversation]
        u = url_from_conversation

        if helpdesk_helper.is_docusaurus_conversation(conversation):
            config = to_docusaurus_config(config, urls)
        elif helpdesk_helper.is_gitbook_conversation(conversation):
            config = to_gitbook_config(config)
        elif helpdesk_helper.is_pkgdown_conversation(conversation):
            config = to_pkgdown_config(config, urls)
        elif helpdesk_helper.is_vuepress_conversation(conversation):
            config = to_vuepress_config(config)
        elif helpdesk_helper.is_larecipe_conversation(conversation):
            config = to_larecipe_config(config, urls)

        config["conversation_id"] = [cuid]

    if '.html' in u:
        urls.append(u.rsplit('/', 1)[0])

    # Use subdomain for github website https://<subdomain>.github.io/
    config['index_name'] = tldextract.extract(
        u).subdomain if tldextract.extract(
        u).domain == 'github' else tldextract.extract(u).domain

    config['start_urls'] = urls

    user_index_name = helpers.get_user_value(
        "index_name is " + "\033[1;33m" + config[
            'index_name'] + "\033[0m" + ' [enter to confirm]: ')

    if user_index_name != "":
        config['index_name'] = user_index_name
        print("index_name is now " + "\033[1;33m" + config[
            'index_name'] + "\033[0m")

    return config
