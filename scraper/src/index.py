"""
documentationSearch scrapper main entry point
"""
from algolia_helper import AlgoliaHelper
from config_loader import ConfigLoader
from documentation_spider import DocumentationSpider
from scrapy.crawler import CrawlerProcess
from strategies.default_strategy import DefaultStrategy
from custom_middleware import CustomMiddleware

try:
    # disable boto (S3 download)
    from scrapy import optional_features

    if 'boto' in optional_features:
        optional_features.remove('boto')
except ImportError:
    pass

CONFIG = ConfigLoader()
CustomMiddleware.driver = CONFIG.driver
DocumentationSpider.NB_INDEXED = 0

if CONFIG.use_anchors:
    import scrapy_patch

STRATEGIES = {
    'default': DefaultStrategy
}

CONFIG_STRATEGY = CONFIG.strategy
if CONFIG_STRATEGY not in STRATEGIES:
    exit("Strategy '" + CONFIG_STRATEGY + "' does not exist")

STRATEGY = STRATEGIES[CONFIG_STRATEGY](CONFIG)

ALGOLIA_HELPER = AlgoliaHelper(
    CONFIG.app_id,
    CONFIG.api_key,
    CONFIG.index_name,
    STRATEGY.get_index_settings()
)

PROCESS = CrawlerProcess({
    'LOG_ENABLED': '1',
    'LOG_LEVEL': 'ERROR',
    # 'LOG_LEVEL': 'DEBUG',
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'DOWNLOADER_MIDDLEWARES': {'__main__.CustomMiddleware': 900},# Need to be > 600 to be after the redirectMiddleware
    'DOWNLOADER_CLIENTCONTEXTFACTORY': 'scrapy_patch.CustomContextFactory'
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

ALGOLIA_HELPER.commit_tmp_index()


print("")
print('Nb hits: ' + str(DocumentationSpider.NB_INDEXED))

CONFIG.update_nb_hits(DocumentationSpider.NB_INDEXED)

print("")
