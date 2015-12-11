"""AlgoliaHelper
Wrapper on top of the AlgoliaSearch API client"""
from algoliasearch import algoliasearch

class AlgoliaHelper:
    """AlgoliaHelper"""
    def __init__(self, app_id, api_key, index_name):
        self.algolia_client = algoliasearch.Client(app_id, api_key)
        self.index_name = index_name
        self.index_name_tmp = index_name + '_tmp'
        self.algolia_index_tmp = self.algolia_client.init_index(self.index_name_tmp)
        self.algolia_client.delete_index(self.index_name_tmp)

    def add_records(self, records):
        """Add new records to the temporary index"""
        record_count = len(records)

        for i in xrange(0, record_count, 50):
            self.algolia_index_tmp.add_objects(records[i:i + 50])

        # print "Pushed records"

    def commit_tmp_index(self, settings):
        """Overwrite the real index with the temporary one"""
        # print "Update settings"
        self.algolia_index_tmp.set_settings(settings)
        self.algolia_client.move_index(self.index_name_tmp, self.index_name)
