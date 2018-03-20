from .abstract_command import AbstractCommand


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

            print file_path + " has been created"

    def config_to_s(self, config):
        import json
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
