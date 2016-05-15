import json
from collections import OrderedDict

import tldextract
import pyperclip
import helpers

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

url = helpers.get_user_value("start url: ")

config['index_name'] = tldextract.extract(url).domain

if helpers.confirm("Does the start_urls require variables ?"):
    config['start_urls'] = [{
        "url": url + ('/' if url[-1] != '/' else '') + '(?P<static_variable>.*?)/(?P<dynamic_variable>.*?)/',
        "variables": {
            "static_variable": [
              "value1",
              "value2"
            ],
            "dynamic_variable": {
              "url": url,
              "js": "var versions = $('#selector option').map(function (i, elt) { return $(elt).html(); }).toArray(); return JSON.stringify(versions);"
            }
        }
    }]
else:
    config['start_urls'] = [url]

dump = json.dumps(config, separators=(',', ': '), indent=2)
pyperclip.copy(dump)

print ""
print "============="
print dump
print "============="
print ""
print "Config copied to clipboard [OK]"
print ""
