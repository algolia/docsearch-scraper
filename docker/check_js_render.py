import json
import os
import sys

config = json.loads(os.environ['CONFIG'])

if 'js_render' in config and config['js_render']:
        sys.exit(0)
else:
        sys.exit(1)
