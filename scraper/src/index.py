"""
DocSearch scraper main entry point
"""

from scrapy.crawler import CrawlerProcess

from .algolia_helper import AlgoliaHelper
from .config.config_loader import ConfigLoader
from .documentation_spider import DocumentationSpider
from .strategies.default_strategy import DefaultStrategy
from .custom_downloader_middleware import CustomDownloaderMiddleware
from .custom_dupefilter import CustomDupeFilter
from .config.browser_handler import BrowserHandler
from .strategies.algolia_settings import AlgoliaSettings
from .scrapy_patch import CustomContextFactory

try:
    # disable boto (S3 download)
    from scrapy import optional_features

    if 'boto' in optional_features:
        optional_features.remove('boto')
except ImportError:
    pass

EXIT_CODE_NO_RECORD = 3


def run_config(config):
    config = ConfigLoader(config)
    CustomDownloaderMiddleware.driver = config.driver
    DocumentationSpider.NB_INDEXED = 0

    strategy = DefaultStrategy(config)

    algolia_helper = AlgoliaHelper(
        config.app_id,
        config.api_key,
        config.index_name,
        AlgoliaSettings.get(config, strategy.levels),
        config.query_rules
    )

    root_module = 'src.' if __name__ == '__main__' else 'scraper.src.'
    DOWNLOADER_MIDDLEWARES_PATH = root_module + 'custom_downloader_middleware.' + CustomDownloaderMiddleware.__name__
    DOWNLOADER_CLIENTCONTEXTFACTORY = root_module + 'scrapy_patch.' + CustomContextFactory.__name__
    DUPEFILTER_CLASS_PATH = root_module + 'custom_dupefilter.' + CustomDupeFilter.__name__

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
        algolia_helper.add_records(config.extra_records, "Extra records", False)

    print("")

    if DocumentationSpider.NB_INDEXED > 0:
        algolia_helper.commit_tmp_index()
        print('Nb hits: {}'.format(DocumentationSpider.NB_INDEXED))
        config.update_nb_hits_value(DocumentationSpider.NB_INDEXED)
    else:
        print('Crawling issue: nbHits 0 for ' + config.index_name)
        algolia_helper.report_crawling_issue()
        exit(EXIT_CODE_NO_RECORD)
    print("")


if __name__ == '__main__':
    from os import environ

    run_config(environ['CONFIG'])
