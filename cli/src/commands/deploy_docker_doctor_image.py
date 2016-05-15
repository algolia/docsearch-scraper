from abstract_command import AbstractCommand


class DeployDockerDoctorImages(AbstractCommand):
    def get_name(self):
        return 'deploy:doctor'

    def get_description(self):
        return 'Deploy docker doctor image'

    def run(self, args):
        self.exec_shell_command(['./cli/scripts/publish_docker_doctor_image.sh'])
