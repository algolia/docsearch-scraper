from abstract_command import AbstractCommand
from os import environ
from build_docker_doctor import BuildDockerDoctor

class RunDoctor(AbstractCommand):
    def get_name(self):
        return 'doctor:run'

    def get_description(self):
        return 'Run the doctor'

    def run(self, args):
        BuildDockerDoctor().run([])

        self.exec_shell_command(["docker", "stop", "documentation-checker"])
        self.exec_shell_command(["docker", "rm", "documentation-checker"])

        config = '{"appId": "' + environ.get('APPLICATION_ID') + '", "apiKey": "' + environ.get('API_KEY') + '", "slackHook": "' + environ.get('SLACK_HOOK') + '", "deployKey": "' + environ.get('DEPLOY_KEY') + '", "schedulerUsername": "' + environ.get('SCHEDULER_USERNAME') + '", "schedulerPassword": "' + environ.get('SCHEDULER_PASSWORD') + '", "websiteUsername": "' + environ.get('WEBSITE_USERNAME') + '", "websitePassword": "' + environ.get('WEBSITE_PASSWORD') + '"}'

        run_command = [
            'docker',
            'run',
            '-e',
            "CONFIG=" + config + "",
            '--name',
            'documentation-checker',
            '-t',
            'algolia/documentation-checker'
        ]

        return self.exec_shell_command(run_command)
