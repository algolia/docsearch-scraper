"""
documentationSearch scrapper main entry point
"""
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader
from documentation_spider import DocumentationSpider
from scrapy.crawler import CrawlerProcess
from strategies.default_strategy import DefaultStrategy
from selenium_middleware import SeleniumMiddleware

# disable boto (S3 download)
from scrapy import optional_features

if 'boto' in optional_features:
    optional_features.remove('boto')

CONFIG = ConfigLoader()
SeleniumMiddleware.driver = CONFIG.driver

if CONFIG.use_anchors:
    import scrappy_patch

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
    # 'LOG_LEVEL': 'DEBUG',
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'DOWNLOADER_MIDDLEWARES': {'__main__.SeleniumMiddleware': 543},
})

PROCESS.crawl(
    DocumentationSpider,
    config=CONFIG,
    algolia_helper=ALGOLIA_HELPER,
    strategy=STRATEGY
)

PROCESS.start()
PROCESS.stop()

CONFIG.destroy()

ALGOLIA_HELPER.commit_tmp_index(STRATEGY.get_index_settings())
