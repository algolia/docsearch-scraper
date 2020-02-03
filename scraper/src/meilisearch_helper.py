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


class MeiliSearchHelper:
    """MeiliSearchHelper"""

    def __init__(self, app_id, api_key, index_uid, settings, query_rules):
        self.meilisearch_client = meilisearch.Client("https://" + app_id + ".getmeili.com" , api_key)
        self.index_uid = index_uid
        self.meilisearch_index = self.meilisearch_client.get_index(self.index_uid)
        self.meilisearch_index.delete_all_documents()
        time.sleep(1)
        # self.meilisearch_index.add_settings(settings)

    def add_records(self, records, url, from_sitemap):
        """Add new records to the temporary index"""
        record_count = len(records)

        for i in range(0, record_count, 50):
            cleaned_records = list(map(clean_dict, records[i:i + 50]))
            self.meilisearch_index.add_documents(cleaned_records)
            # self.meilisearch_index.add_documents(records[i:i + 50])

        color = "96" if from_sitemap else "94"

        print(
            '\033[{}m> DocSearch: \033[0m{}\033[93m {} records\033[0m)'.format(
                color, url, record_count))
