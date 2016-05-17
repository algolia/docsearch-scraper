from abstract_command import AbstractCommand


class BuildDockerScraper(AbstractCommand):
    def get_name(self):
        return 'docker:build-scraper'

    def get_description(self):
        return 'Build scraper images (dev, prod, test)'

    def run(self, args):
        code = self.build_docker_file("scraper/dev/docker/Dockerfile.base")
        if code != 0:
            return code
        code = self.build_docker_file("scraper/dev/docker/Dockerfile.dev")
        if code != 0:
            return code
        return self.build_docker_file("scraper/dev/docker/Dockerfile")
