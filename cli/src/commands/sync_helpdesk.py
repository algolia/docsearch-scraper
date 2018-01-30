from .abstract_command import AbstractCommand


class SyncHelpdesk(AbstractCommand):
    def get_name(self):
        return 'sync:helpdesk'

    def get_description(self):
        return 'update conversation for the missing config (conversation ID)'

    def get_usage(self):
        return super(SyncHelpdesk, self).get_usage() + " config"

    def run(self, args):
        from sync.src.sync_helpdesk import sync_helpdesk

        # self.check_not_docsearch_app_id('run a config manually')
        return sync_helpdesk(args)
