"""
Abstract Strategy
"""
class AbstractStrategy(object):
    """
    Abstract Strategy
    """

    def __init__(self, config):
        self.config = config

    def get_settings(self):
        raise Exception('get_settings need to be implemented')

    def create_objects_from_document(self):
        raise Exception('create_objects_from_document need to be implemented')
