"""MeiliSearchHelper
Wrapper on top of the AlgoliaSearch API client"""

import time
import meilisearch
from builtins import range

def clean_one_field(value):
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return str(value)
    return value

def clean_dict(record):
    for key, value in record.items():
        if isinstance(value, dict):
            record[key] = clean_dict(value)
        else:
            record[key] = clean_one_field(value)
    return record

def parse_weight(record):
    new = {}
    for key, value in record.items():
        if key == 'weight':
            for k, v in value.items():
                new[k] = v
    del record['weight']
    return {**record, **new}

class MeiliSearchHelper:
    """MeiliSearchHelper"""

    # Go to scraper/src/strategy/algolia_settings.py to understand criteria order
    SETTINGS = {
        "rankingOrder": [
            "_number_of_words",
            "_sum_of_typos",
            "_sum_of_words_attribute",
            "_word_proximity",
            "_exact",
            "page_rank",
            "level",
            "position"
        ],
        "distinctField": "url",
        "rankingRules": {
            "page_rank": "dsc",
            "level": "dsc",
            "position": "asc"
        }
    }

    # Schema updated manually. Here is the schema:
    # SCHEMA = {
    #     "anchor": ["displayed"],
    #     "content":  ["indexed", "displayed"],
    #     "hierarchy": ["indexed", "displayed"],
    #     "hierarchy_radio": ["indexed"],
    #     "type":  [],
    #     "tags":  [],
    #     "url":  ["displayed"],
    #     "url_without_variables":  [],
    #     "hierarchy_camel":  ["indexed"],
    #     "hierarchy_radio_camel":  ["indexed"],
    #     "content_camel":  [],
    #     "lang":  [],
    #     "url_without_anchor": [],
    #     "no_variables":  [],
    #     "objectID": ["identifier", "indexed"],
    #     "page_rank":  ["indexed", ranked"],
    #     "level":  ["indexed", "ranked"],
    #     "position":  ["indexed" "ranked"]
    # }

    def __init__(self, app_id, api_key, index_uid):
        self.meilisearch_client = meilisearch.Client("https://" + app_id + ".getmeili.com" , api_key)
        self.index_uid = index_uid
        self.meilisearch_index = self.meilisearch_client.get_index(self.index_uid)
        self.meilisearch_index.delete_all_documents()
        time.sleep(1)
        self.meilisearch_index.add_settings(MeiliSearchHelper.SETTINGS)

    def add_records(self, records, url, from_sitemap):
        """Add new records to the temporary index"""
        record_count = len(records)

        for i in range(0, record_count, 50):
            parsed_records = list(map(parse_weight, records[i:i + 50]))
            cleaned_records = list(map(clean_dict, parsed_records))
            self.meilisearch_index.add_documents(cleaned_records)

        color = "96" if from_sitemap else "94"

        print(
            '\033[{}m> DocSearch: \033[0m{}\033[93m {} records\033[0m)'.format(
                color, url, record_count))
