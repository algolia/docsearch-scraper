import scrapy
import lxml
from lxml.cssselect import CSSSelector
import json
import sys
import re

class DocumentationSpyder(scrapy.Spider):
    def __init__(self):
        self.load_config(sys.argv[1])

    def parse(self, response):
        self.scrap_content(response)


        #for href in response.css("a::attr('href')"):
            #url = response.urljoin(href.extract())
            #yield scrapy.Request(url, callback=self.parse)

    def scrap_content(self, response):
        selectors = [
            "#content header h1",
            "#content header p",
            "#content section h1",
            "#content section h2",
            "#content section h3",
            "#content section h4",
            "#content section h5",
            "#content section h6",
            "#content section p",
            "#content section ol"
        ]

        doc = lxml.html.fromstring(response.body)

        separate_results = {}

        for selector in selectors:
            separate_selector = CSSSelector(selector)
            separate_results[selector] = separate_selector(doc)

        sel = CSSSelector(','.join(selectors))

        for el in sel(doc):
            current_selector = ''
            for selector in selectors:
                if self.findMatchingElem(el, separate_results[selector]):
                    current_selector = selector
                    break

            print ">" + self.get_element_content(el) + "< (" + current_selector + ")"

    def findMatchingElem(self, el, l):
        for elem in l:
            if el.getroottree().getpath(el) == elem.getroottree().getpath(elem):
                return True
        return False


    def get_element_content(self, el):
        s = ""

        for x in el.itertext():
            s = s + re.sub('\s+', ' ', x.strip(' \t\n\r'))

        return s


    def load_config(self, filepath):
        config = json.loads(open(filepath, "r").read())

        self.name = config.get("name")
        self.allowed_domains = config.get("allowed_domains")
        self.start_urls = config.get("start_urls")