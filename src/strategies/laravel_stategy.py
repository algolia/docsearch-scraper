import copy
from urlparse import urlparse
from strategy import AbstactStrategy


class LaravelStrategy(AbstactStrategy):

    def get_settings(self):
        attributes_to_index = ['unordered(title)']
        attributes_to_highlight = ['title']
        attributes_to_retrieve = ['title']

        for i in range(1, len(self.config.get_selectors())):
            attributes_to_index.append('unordered(h' + str(i) + ')')
            attributes_to_highlight.append('h' + str(i))
            attributes_to_retrieve.append('h' + str(i))

        attributes_to_index += ['content', 'path', 'hash']
        attributes_to_highlight += ['content']
        attributes_to_retrieve += ['_tags', 'link']

        return {
            'attributesToIndex'         : attributes_to_index,
            'attributesToHighlight'     : attributes_to_highlight,
            'attributesToRetrieve'      : attributes_to_retrieve,
            'attributesToSnippet'       : ['content:50'],
            'customRanking'             : ['asc(importance)'],
            'ranking'                   : ['words', 'typo', 'attribute', 'proximity', 'exact', 'custom'],
            'minWordSizefor1Typo'       : 3,
            'minWordSizefor2Typos'      : 7,
            'allowTyposOnNumericTokens' : False,
            'minProximity'              : 2,
            'ignorePlurals'             : True,
            'advancedSyntax'            : True,
            'removeWordsIfNoResults'    : 'allOptional'
        }

    def create_objects_from_document(self, blocs, response):
        objects = []
        current_blocs = {}

        for i in range(0, len(self.selectors)):
            current_blocs[self.get_key(i)] = None

        for ((el, bloc), importance) in blocs:
            for i in range(importance, len(self.selectors)):
                current_blocs[self.get_key(i)] = None

            current_blocs[self.get_key(importance)] = bloc
            current_blocs['importance'] = self.get_importance(current_blocs)
            current_blocs['link'] = response.url + self.get_hash(el)
            current_blocs['hash'] = self.get_hash(el)
            current_blocs['path'] = urlparse(current_blocs['link']).path

            objects.append(copy.deepcopy(current_blocs))

        return objects

    def get_key(self, i):
        if i == 0:
            return 'title'
        if i == (len(self.selectors) - 1):
            return 'content'
        return 'h' + str(i)

    def get_importance(self, current_blocs):
        importance = -1
        for i in range(0, len(self.selectors)):
            if current_blocs.get(self.get_key(i)) is not None:
                importance += 1

        return importance

    def get_hash(self, el):
        current_el = el

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        while current_el.getprevious() is not None and current_el.get('id', default=None) is None:
            current_el = current_el.getprevious()

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        while current_el.getparent() is not None and current_el.get('id', default=None) is None:
            current_el = current_el.getparent()

        if (current_el.get('id', default=None)) is not None:
            return '#' + current_el.get('id')

        return ""

