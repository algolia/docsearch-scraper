import sys
from os import getcwd, path, environ
from dotenv import load_dotenv

env_file = getcwd() + '/.env'
load_dotenv(env_file)

from helpers import get_color
from helpers import printer
from helpers import print_error
from helpers import print_command_help

from commands.bootstrap_config import BootstrapConfig
from commands.install_dependencies import InstallDependencies
from commands.playground_config import PlaygroundConfig
from commands.help import Help
from commands.build_docker_scraper import BuildDockerScraper
from commands.build_docker_doctor import BuildDockerDoctor
from commands.run_tests import RunTests
from commands.run_config import RunConfig
from commands.deploy_docker_scraper_images import DeployDockerScraperImages
from commands.deploy_docker_doctor_image import DeployDockerDoctorImages
from commands.deploy_configs import DeployConfigs
from commands.run_config_docker import RunConfigDocker
from commands.run_doctor import RunDoctor
from commands.reindex_connector import ReindexConnector

if not path.isfile(env_file):
    print ""
    print "No .env found. Let's create one."

    f = open(env_file, "w")

    ans = raw_input("What is your Algolia APPLICATION_ID: ")
    f.write("APPLICATION_ID=" + ans + "\n")

    ans = raw_input("What is your Algolia API_KEY: ")
    f.write("API_KEY=" + ans + "\n")

    ans = raw_input("What is your WEBSITE_USERNAME (Leave empty if you are not an Algolia employee): ")
    f.write("WEBSITE_USERNAME=" + ans + "\n")

    ans = raw_input("What is your WEBSITE_PASSWORD (Leave empty if you are not an Algolia employee): ")
    f.write("WEBSITE_PASSWORD=" + ans + "\n")

    ans = raw_input("What is your SLACK_HOOK (Leave empty unless you have it): ")
    if ans != "":
        f.write("SLACK_HOOK=" + ans + "\n")

        ans = raw_input("What is your DEPLOY_KEY (Leave empty unless you have it): ")
        f.write("DEPLOY_KEY=" + ans + "\n")

    f.close()

    print ""

load_dotenv(env_file)

ADMIN = True
CREDENTIALS = True

if 'APPLICATION_ID' not in environ or len(environ['APPLICATION_ID']) == 0:
    CREDENTIALS = False

if 'API_KEY' not in environ or len(environ['API_KEY']) == 0:
    CREDENTIALS = False

if 'WEBSITE_USERNAME' not in environ or len(environ['WEBSITE_USERNAME']) == 0:
    ADMIN = False

if 'WEBSITE_PASSWORD' not in environ or len(environ['WEBSITE_PASSWORD']) == 0:
    ADMIN = False


cmds = []

cmds.append(BootstrapConfig())
cmds.append(InstallDependencies())
cmds.append(Help())
cmds.append(BuildDockerScraper())
cmds.append(BuildDockerDoctor())
cmds.append(RunTests())
cmds.append(PlaygroundConfig())
cmds.append(ReindexConnector())

if CREDENTIALS:
    cmds.append(RunConfig())
    cmds.append(RunConfigDocker())

if ADMIN:
    cmds.append(DeployConfigs())
    cmds.append(DeployDockerScraperImages())
    cmds.append(DeployDockerDoctorImages())
    cmds.append(RunDoctor())


def print_usage():
    printer("Docsearch CLI", 1)
    printer("")
    printer("Usage:", 2)
    printer("  ./docsearch command [options] [arguments]")
    printer("")
    printer("Options:", 2)
    printer("  " + get_color(1) + "--help" + get_color() + (' ' * 4) + 'Display help message')

    printer("")

    groups = {}

    longest_cmd_name = 0

    for cmd in cmds:
        longest_cmd_name = max(longest_cmd_name, len(cmd.get_name()))
        group = ''

        if ':' in cmd.get_name():
            group = cmd.get_name().split(':')[0]

        if group not in groups:
            groups[group] = []

        groups[group].append(cmd)

    printer("Available commands:", 2)

    for key in sorted(groups.keys()):
        if key != "":
            printer(" " + key, 2)
        for cmd in groups[key]:
            nb_spaces = longest_cmd_name + 2 - len(cmd.get_name())
            printer("  " + get_color(1) + cmd.get_name() + get_color() + (' ' * nb_spaces) + cmd.get_description())

def find_command(name, cmds):
    for cmd in cmds:
        if cmd.get_name().find(name) == 0:
            return cmd

    return None

if len(sys.argv) == 1:
    print_usage()
else:
    help_needed = "--help" in sys.argv

    if help_needed:
        del sys.argv[sys.argv.index("--help")]

    command = find_command(sys.argv[1], cmds)

    if command is not None:
        if help_needed:
            print_command_help(command)
        else:
            if len(sys.argv[2:]) < len(command.get_options()):
                printer("")
                print_error("Missing at least one argument")
                printer("")
                print_command_help(command)
            else:
                exit(command.run(sys.argv[2:]))
    else:
        print_error("Command \"" + sys.argv[1] + "\" not found")

exit(1)
