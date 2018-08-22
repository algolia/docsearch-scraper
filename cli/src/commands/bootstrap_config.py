from .abstract_command import AbstractCommand
from collections import OrderedDict


class BootstrapConfig(AbstractCommand):
    def get_name(self):
        return 'bootstrap'

    def get_description(self):
        return 'Bootstrap a DocSearch config'

    def run(self, args):
        from os import environ, path
        from deployer.src.config_creator import create_config

        if len(args) > 0 and "http" in args[0]:
            config = create_config(args[0])
        else:
            config = create_config()

        config_folder = environ.get('PUBLIC_CONFIG_FOLDER')

        if config_folder is None:
            self.print_config(config)
        else:
            if not path.isdir(config_folder):
                self.print_config(config)
                print("Folder: " + config_folder + " does not exist")
                return

            file_path = config_folder + "/" + config['index_name'] + ".json"

            if path.isfile(file_path):
                self.print_config(config)
                print("File: " + file_path + " already exists")
                return

            file = open(file_path, "w")
            file.write(self.config_to_s(config))
            file.close()

            print(file_path + " has been created")

    def config_to_s(self, config):
        import json
        config = OrderedDict(sorted(config.items(),
                                  key=key_sort)
                           )

        return json.dumps(config, separators=(',', ': '), indent=2)

    def print_config(self, config):
        import pyperclip

        dump = self.config_to_s(config)
        pyperclip.copy(dump)

        print("")
        print("=============")
        print(dump)
        print("=============")
        print("")
        print("Config copied to clipboard [OK]")
        print("")


def key_sort(attr):
    ref = {
        "index_name": 0,
        "start_urls": 1,
        "sitemap_urls": 2,
        "sitemap_urls_regexs": 3,
        "sitemap_alternate_links": 4,
        "stop_urls": 5,
        "force_sitemap_urls_crawling": 6,
        "strict_redirects": 7,
        "selectors": 8,
        "selectors_exclude": 9,
        "stop_content": 10,
        "strip_chars": 11,
        "keep_tags": 12,
        "min_indexed_level": 13,
        "only_content_level": 14,
        "js_render": 15,
        "js_wait": 16,
        "use_anchors": 17,
        "custom_settings": 18,
        "synonyms": 19,
        "docker_memory": 20,
        "docker_cpu": 21,
        "conversation_id": 22,
        "comments": 29,
        "nb_hits": 30
    }
    if attr[0] in ref.keys():
        return ref[attr[0]]
    else:
        return 27
