from .abstract_build_docker import AbstractBuildDocker


class BuildDockerScraper(AbstractBuildDocker):
    def get_name(self):
        return 'docker:build'

    def get_description(self):
        return 'Build scraper images (dev, prod)'

    def run(self, args):

        code = self.build_docker_file("scraper/dev/docker/Dockerfile.base",
                                      "algolia/base-documentation-scraper")
        if code != 0:
            return code
        code = self.build_docker_file("scraper/dev/docker/Dockerfile.dev",
                                      python3=py3)
        if code != 0:
            return code
        return self.build_docker_file("scraper/dev/docker/Dockerfile",
                                      "algolia/documentation-scraper")
