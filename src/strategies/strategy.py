class AbstactStrategy:
    def __init__(self, config, selectors, custom_settings):
        self.config = config
        self.selectors = selectors
        self.custom_settings = custom_settings

    def get_settings(self):
        raise Exception('get_settings need to be implemented')

    def create_objects_from_document(self, blocs, response, tags, page_ranks):
        raise Exception('index_document need to be implemented')
