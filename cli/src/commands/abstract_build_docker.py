from .abstract_command import AbstractCommand


class AbstractBuildDocker(AbstractCommand):
    @staticmethod
    def build_docker_file(file, image="algolia/docsearch-scraper-dev"):
        cmd = ["docker", "build", "-t", image, "-f", file, "."]
        return AbstractCommand.exec_shell_command(cmd)
