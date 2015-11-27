"""
documentationSearch scrapper main entry point
"""
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader
from documentation_spyder import DocumentationSpyder
from scrapy.crawler import CrawlerProcess
from strategies.default_strategy import DefaultStrategy

CONFIG = ConfigLoader()

ALGOLIA_HELPER = AlgoliaHelper(
    CONFIG.app_id,
    CONFIG.api_key,
    CONFIG.index_name
)

STRATEGIES = {
    'default': DefaultStrategy
}

CONFIG_STRATEGY = CONFIG.strategy
if not CONFIG_STRATEGY in STRATEGIES:
    exit("Strategy '" + CONFIG_STRATEGY + "' does not exist")

STRATEGY = STRATEGIES[CONFIG_STRATEGY](CONFIG)

PROCESS = CrawlerProcess({
    'LOG_ENABLED': '1',
    'LOG_LEVEL': 'ERROR',
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
PROCESS.crawl(
    DocumentationSpyder,
    index_name=CONFIG.index_name,
    allowed_domains=CONFIG.allowed_domains,
    start_urls=CONFIG.start_urls,
    stop_urls=CONFIG.stop_urls,
    selectors=CONFIG.selectors,
    selectors_exclude=CONFIG.selectors_exclude,
    strip_chars=CONFIG.strip_chars,
    algolia_helper=ALGOLIA_HELPER,
    strategy=STRATEGY
)
#
# PROCESS.start()
# PROCESS.stop()
#
# ALGOLIA_HELPER.move_index_with_settings(STRATEGY.get_settings())
