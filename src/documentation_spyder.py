import scrapy
import lxml
from lxml.cssselect import CSSSelector
import json
import sys
import re

class DocumentationSpyder(scrapy.Spider):
    def __init__(self):
        config = json.loads(open(sys.argv[1], "r").read())

        self.name = config.get("name")
        self.allowed_domains = config.get("allowed_domains")
        self.start_urls = config.get("start_urls")
        self.selectors = config.get("selectors")

    def parse(self, response):
        self.scrap_content(response)

        #for href in response.css("a::attr('href')"):
            #url = response.urljoin(href.extract())
            #yield scrapy.Request(url, callback=self.parse)

    def scrap_content(self, response):
        doc = lxml.html.fromstring(response.body)

        separate_results = {}

        for selector in self.selectors:
            separate_selector = CSSSelector(selector)
            separate_results[selector] = separate_selector(doc)

        sel = CSSSelector(','.join(self.selectors))

        blocs = []

        for el in sel(doc):
            current_selector = ''
            for selector in self.selectors:
                if self.findMatchingElem(el, separate_results[selector]):
                    current_selector = selector
                    break
            blocs.append((self.get_element_content(el), self.selectors.index(current_selector)))

        self.index_document(blocs, response)



    def index_document(self, blocs, response):
        last_importance = -1

        current_blocs = []

        for i, selector in enumerate(self.selectors):
            current_blocs[i] = None

        for (bloc, importance) in blocs:
            print bloc, importance

    def findMatchingElem(self, el, l):
        for elem in l:
            if el.getroottree().getpath(el) == elem.getroottree().getpath(elem):
                return True
        return False

    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s += re.sub('\s+', ' ', x.strip(' \t\n\r'))

        return s