from abstract_command import AbstractCommand

class DeployDockerImages(AbstractCommand):
    def get_name(self):
        return 'deploy:images'

    def get_description(self):
        return 'Deploy docker images (scraper + doctor)'

    def run(self, args):
        self.exec_shell_command(['./cli/scripts/publish_docker_images.sh'])
