"""
documentationSearch scrapper main entry point
"""
from scrapy.crawler import CrawlerProcess
from documentation_spyder import DocumentationSpyder
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader
from strategies.laravel_stategy import LaravelStrategy

CONFIG = ConfigLoader()

ALGOLIA_HELPER = AlgoliaHelper(
    CONFIG.get_app_id(),
    CONFIG.get_api_key(),
    CONFIG.get_index_name()
)

STRATEGIES = {
    'laravel': LaravelStrategy
}

CONFIG_STRATEGY = CONFIG.get_strategy()
if not CONFIG_STRATEGY in STRATEGIES:
    exit("'" + CONFIG_STRATEGY + "' is not a good strategy name")

# TODO: Only need to pass CONFIG, all the others can be found from CONFIG
STRATEGY = STRATEGIES[CONFIG_STRATEGY](
    CONFIG,
    CONFIG.get_selectors(),
    CONFIG.get_custom_settings(),
    CONFIG.get_hash_strategy()
)

PROCESS = CrawlerProcess({
    'LOG_ENABLED': '1',
    'LOG_LEVEL': 'ERROR',
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
PROCESS.crawl(
    DocumentationSpyder,
    index_name=CONFIG.get_index_name(),
    allowed_domains=CONFIG.get_allowed_domains(),
    start_urls=CONFIG.get_start_urls(),
    stop_urls=CONFIG.get_stop_urls(),
    selectors=CONFIG.get_selectors(),
    selectors_exclude=CONFIG.get_selectors_exclude(),
    strip_chars=CONFIG.get_strip_chars(),
    algolia_helper=ALGOLIA_HELPER,
    strategy=STRATEGY
)

PROCESS.start()
PROCESS.stop()

ALGOLIA_HELPER.move_index_with_settings(STRATEGY.get_settings())
