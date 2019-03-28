from .abstract_build_docker import AbstractBuildDocker


class BuildDockerScraper(AbstractBuildDocker):
    def get_name(self):
        return "docker:build"

    def get_description(self):
        return "Build scraper images (dev, prod)"

    def get_options(self):
        return [{"name": "test",
                 "description": "build the test image",
                 "optional": False}]

    def run(self, args):

        test = self.get_option("test", args)

        if test:
            return self.build_docker_file("scraper/dev/docker/Dockerfile.test",
                                          "algolia/docsearch-scraper-test")

        code = self.build_docker_file("scraper/dev/docker/Dockerfile.base",
                                      "algolia/docsearch-scraper-base")

        if code != 0:
            return code
        code = self.build_docker_file("scraper/dev/docker/Dockerfile.dev")
        if code != 0:
            return code
        return self.build_docker_file("scraper/dev/docker/Dockerfile",
                                      "algolia/docsearch-scraper")
