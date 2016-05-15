from abstract_command import AbstractCommand


class BuildDockerScraper(AbstractCommand):
    def get_name(self):
        return 'docker:build-scraper'

    def get_description(self):
        return 'Build scraper images (dev, prod, test)'

    def run(self, args):
        self.build_docker_file("scraper/dev/docker/Dockerfile.base")
        self.build_docker_file("scraper/dev/docker/Dockerfile.dev")
        self.build_docker_file("scraper/dev/docker/Dockerfile")
