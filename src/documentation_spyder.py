import scrapy
import os
import json
import sys

class DocumentationSpyder(scrapy.Spider):
    def __init__(self):
        self.load_config(sys.argv[1])

    def getFileNameFromUrl(self, url):
        filename = url.replace('//', '-').replace('/', '-').replace(':', '').replace('.', '-')

        return "crawling_data/" + self.name + "/" + filename

    def saveResponseToFile(self, response):
        with open(self.getFileNameFromUrl(response.url), 'wb') as f:
            f.write(response.body)

    def parse(self, response):
        self.saveResponseToFile(response)

        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

    def load_config(self, filepath):
        config = json.loads(open(filepath, "r").read())

        self.name = config.get("name")
        self.allowed_domains = config.get("allowed_domains")
        self.start_urls = config.get("start_urls")

        if not os.path.exists("crawling_data/" + self.name):
            os.makedirs("crawling_data/" + self.name)