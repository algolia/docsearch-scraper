from abstract_command import AbstractCommand


class BuildDockerDoctor(AbstractCommand):
    def get_name(self):
        return 'docker:build-doctor'

    def get_description(self):
        return 'Build doctor image'

    def run(self, args):
        self.build_docker_file("doctor/dev/docker/Dockerfile", "algolia/documentation-checker")
