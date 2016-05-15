import json
import os
import sys
import re

conf = os.environ['CONFIG']
config = json.loads(conf)

group_regex = re.compile("\\(\?P<(.+?)>.+?\\)")
results = re.findall(group_regex, conf)

if ('js_render' in config and config['js_render']) or len(results) > 0:
        sys.exit(0)
else:
        sys.exit(1)
