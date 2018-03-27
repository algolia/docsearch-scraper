from .abstract_command import AbstractCommand


class BatchSyncHelpdesk(AbstractCommand):
    def get_name(self):
        return 'batch:sync_helpdesk'

    def get_description(self):
        return 'update conversation for the missing config (conversation ID)'

    def get_usage(self):
        return super(BatchSyncHelpdesk, self).get_usage() + " config"

    def run(self, args):
        from batch.src.batch_sync_helpdesk import batch_sync_helpdesk

        return batch_sync_helpdesk(args)
