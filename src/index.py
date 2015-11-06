from scrapy.crawler import CrawlerProcess
from documentation_spyder import DocumentationSpyder
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader
from strategies.laravel_stategy import LaravelStrategy

config = ConfigLoader()

algolia_helper = AlgoliaHelper(
                    config.get_app_id(),
                    config.get_api_key(),
                    config.get_index_name())

strategies = {
    'laravel': LaravelStrategy
}

if not config.get_strategy() in strategies:
    exit("'" + config.get_strategy() + "' is not a good strategy name")

strategy = strategies[config.get_strategy()](config, config.get_selectors(), config.get_custom_settings(),
                                             config.get_hash_strategy())

process = CrawlerProcess({'LOG_ENABLED': '1', 'LOG_LEVEL': 'ERROR', 'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process.crawl(DocumentationSpyder,
                index_name=config.get_index_name(),
                allowed_domains=config.get_allowed_domains(),
                start_urls=config.get_start_urls(),
                stop_urls=config.get_stop_urls(),
                selectors=config.get_selectors(),
                selectors_exclude=config.get_selectors_exclude(),
                strip_chars=config.get_strip_chars(),
                algolia_helper=algolia_helper,
                strategy=strategy)

process.start()
process.stop()

algolia_helper.move_index_with_settings(strategy.get_settings())
