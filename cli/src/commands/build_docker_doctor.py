from abstract_build_docker import AbstractBuildDocker


class BuildDockerDoctor(AbstractBuildDocker):
    def get_name(self):
        return 'docker:build-doctor'

    def get_description(self):
        return 'Build doctor image'

    def get_options(self):
        return []

    def run(self, args):
        return self.build_docker_file("doctor/dev/docker/Dockerfile", "algolia/documentation-checker")
