from collections import OrderedDict
import json
import tldextract
import pyperclip
import helpers

from html_helper import get_main_selector

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
