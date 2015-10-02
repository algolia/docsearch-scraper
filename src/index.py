import sys
import os.path
from scrapy.crawler import CrawlerProcess
from documentation_spyder import DocumentationSpyder

if len(sys.argv) != 2:
    print("Usage:\n$ index.py config.json")
    exit()

if os.path.isfile(sys.argv[1]) == False:
    print("Wrong path for the config path")
    exit()

if not os.path.exists("crawling_data"):
    os.makedirs("crawling_data")

process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
process.crawl(DocumentationSpyder)
process.start()
process.stop()
