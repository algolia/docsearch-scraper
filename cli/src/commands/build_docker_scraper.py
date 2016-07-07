from .abstract_build_docker import AbstractBuildDocker


class BuildDockerScraper(AbstractBuildDocker):
    def get_name(self):
        return 'docker:build-scraper'

    def get_description(self):
        return 'Build scraper images (dev, prod, test)'

    def run(self, args):
        py3 = self.get_option('python3', args)

        code = self.build_docker_file("scraper/dev/docker/Dockerfile.base", "algolia/base-documentation-scrapper")
        if code != 0:
            return code
        code = self.build_docker_file("scraper/dev/docker/Dockerfile.dev", python3=py3)
        if code != 0:
            return code
        return self.build_docker_file("scraper/dev/docker/Dockerfile", "algolia/documentation-scrapper", py3)
