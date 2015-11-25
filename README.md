# Documentation scrapper

## Getting started for OSX

Run the following commands :

- `brew install python # will install pip`
- `pip install scrapy`
- `pip install algoliasearch`
- `git clone git@github.com:algolia/documentation-scrapper.git`
- `cd documentation-scrapper`

## Run the scrapper

Usage:
```sh
$ APPLICATION_ID=app_id API_KEY=api_key INDEX_PREFIX=prefix_ CONFIG="`cat configs/stripe.json`" python src/index.py
```

The config.json should look like:

```json
{
    "index_name": "stripe",
    "allowed_domains": ["stripe.com"],
    "start_urls": [
        "https://stripe.com/docs",
        "https://stripe.com/docs/api[tags:api][page_rank:1]",
        "https://stripe.com/help[tags:help]"
    ],
    "stop_urls": [
        "https://stripe.com/docs/api/"
    ],
    "selectors_exclude": [
        ".method-list"
    ],
    "selectors": [
        ["#content header h1", "#content section h1"],
        ["#content section h2"],
        ["#content section h3"],
        ["#content section h4"],
        ["#content section h5"],
        ["#content section h6"],
        ["#content header p", "#content section p", "#content section ol"]
    ],
    "custom_settings": {},
    "hash_strategy": "id",
    "strategy": "laravel"
}
```

## Docker

You might want a script like this to build and run the docker container

```sh
#!/bin/bash

docker build -t algolia/documentation-scrapper . || exit 1

docker stop documentation-scrapper > /dev/null 2>&1 || true
docker rm documentation-scrapper > /dev/null 2>&1 || true

docker run \
    -e APPLICATION_ID=app_id \
    -e API_KEY=api_key \
    -e INDEX_PREFIX=prefix_ \
    -e CONFIG="`cat configs/stripe.json`" \
    --name documentation-scrapper \
    -t algolia/documentation-scrapper /root/run
```
