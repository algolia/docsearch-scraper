"""
documentationSearch scrapper main entry point
"""

from scrapy.crawler import CrawlerProcess

from .algolia_helper import AlgoliaHelper
from .config.config_loader import ConfigLoader
from .documentation_spider import DocumentationSpider
from .strategies.default_strategy import DefaultStrategy
from .custom_middleware import CustomMiddleware
from .config.browser_handler import BrowserHandler
from .strategies.algolia_settings import AlgoliaSettings

try:
    # disable boto (S3 download)
    from scrapy import optional_features

    if 'boto' in optional_features:
        optional_features.remove('boto')
except ImportError:
    pass


def run_config(config):
    config = ConfigLoader(config)
    CustomMiddleware.driver = config.driver
    DocumentationSpider.NB_INDEXED = 0

    if config.use_anchors:
        from . import scrapy_patch

    strategy = DefaultStrategy(config)

    algolia_helper = AlgoliaHelper(
        config.app_id,
        config.api_key,
        config.index_name,
        AlgoliaSettings.get(config, strategy.levels)
    )

    DOWNLOADER_MIDDLEWARES_PATH = 'scraper.src.custom_middleware.CustomMiddleware'
    DOWNLOADER_CLIENTCONTEXTFACTORY = 'scraper.src.scrapy_patch.CustomContextFactory'
    DUPEFILTER_CLASS_PATH = 'scraper.src.custom_dupefilter.CustomDupeFilter'

    if __name__ == '__main__':
        DOWNLOADER_MIDDLEWARES_PATH = 'src.custom_middleware.CustomMiddleware'
        DOWNLOADER_CLIENTCONTEXTFACTORY = 'src.scrapy_patch.CustomContextFactory'
        DUPEFILTER_CLASS_PATH = 'src.custom_dupefilter.CustomDupeFilter'

    process = CrawlerProcess({
        'LOG_ENABLED': '1',
        'LOG_LEVEL': 'ERROR',
        'USER_AGENT': config.user_agent,
        'DOWNLOADER_MIDDLEWARES': {DOWNLOADER_MIDDLEWARES_PATH: 900},
        # Need to be > 600 to be after the redirectMiddleware
        'DOWNLOADER_CLIENTCONTEXTFACTORY': DOWNLOADER_CLIENTCONTEXTFACTORY,
        'DUPEFILTER_USE_ANCHORS': config.use_anchors,
        # Use our custom dupefilter in order to be scheme agnostic regarding link provided
        'DUPEFILTER_CLASS': DUPEFILTER_CLASS_PATH
    })

    process.crawl(
        DocumentationSpider,
        config=config,
        algolia_helper=algolia_helper,
        strategy=strategy
    )

    process.start()
    process.stop()

    # Kill browser if needed
    BrowserHandler.destroy(config.driver)

    if len(config.extra_records) > 0:
        algolia_helper.add_records(config.extra_records, "Extra records")

    print("")

    if DocumentationSpider.NB_INDEXED > 0:
        algolia_helper.commit_tmp_index()
        print('Nb hits: ' + str(DocumentationSpider.NB_INDEXED))
        config.update_nb_hits(DocumentationSpider.NB_INDEXED)
    else:
        print('Crawling issue: nbHits 0 for ' + config.index_name)
        algolia_helper.report_crawling_issue()

    print("")

if __name__ == '__main__':
    from os import environ
    run_config(environ['CONFIG'])
