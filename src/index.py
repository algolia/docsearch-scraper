from scrapy.crawler import CrawlerProcess
from documentation_spyder import DocumentationSpyder
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader

config = ConfigLoader()

algolia_helper = AlgoliaHelper(
                    config.get_app_id(),
                    config.get_api_key(),
                    config.get_index_name())

process = CrawlerProcess({'LOG_ENABLED': '1', 'LOG_LEVEL': 'ERROR', 'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process.crawl(DocumentationSpyder,
                index_name=config.get_index_name(),
                allowed_domains=config.get_allowed_domains(),
                start_urls=config.get_start_urls(),
                stop_urls=config.get_stop_urls(),
                selectors=config.get_selectors(),
                algolia_helper=algolia_helper)
process.start()
process.stop()

attributes_to_index = ['unordered(title)']
attributes_to_highlight = ['title']
attributes_to_retrieve = ['title']

for i in range(1, len(config.get_selectors())):
    attributes_to_index.append('unordered(h' + str(i) + ')')
    attributes_to_highlight.append('h' + str(i))
    attributes_to_retrieve.append('h' + str(i))

attributes_to_index += ['content', 'path', 'hash']
attributes_to_highlight += ['content']
attributes_to_retrieve += ['_tags', 'link']

settings = {
    'attributesToIndex'         : attributes_to_index,
    'attributesToHighlight'     : attributes_to_highlight,
    'attributesToRetrieve'      : attributes_to_retrieve,
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

algolia_helper.move_index_with_settings(settings)
