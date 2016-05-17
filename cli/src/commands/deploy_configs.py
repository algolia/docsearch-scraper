from abstract_command import AbstractCommand
from build_docker_scraper import BuildDockerScraper
from build_docker_doctor import BuildDockerDoctor

class DeployConfigs(AbstractCommand):
    def get_name(self):
        return 'deploy:configs'

    def get_description(self):
        return 'Deploy configs'

    def run(self, args):
        return self.exec_shell_command(['./deployer/deploy'])
