from algoliasearch import algoliasearch

class AlgoliaHelper:
    def __init__(self, app_id, api_key, index_name):
        self.algolia_client = algoliasearch.Client(app_id, api_key)
        self.index_name = index_name
        self.algolia_index_tmp = self.algolia_client.init_index(index_name + '_tmp')
        self.algolia_client.delete_index(index_name + '_tmp')

    def add_objects(self, objects):
        self.algolia_index_tmp.add_objects(objects)

    def move_index_with_settings(self, settings):
        self.algolia_index_tmp.set_settings(settings)
        self.algolia_client.move_index(self.index_name + '_tmp', self.index_name)