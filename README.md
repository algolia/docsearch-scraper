# Documentation scrapper

## Getting started for OSX

Run the following commands :

- ```brew install python # will install pip```
- ```pip install scrapy```
- ```git clone git@github.com:algolia/documentation-scrapper.git```
- ```cd documentation-scrapper```

## Run the scrapper

Usage: $ ```APPLICATION_ID=app_id API_KEY=api_key INDEX_PREFIX=prefix_ CONFIG="`cat configs/stripe.json`" python src/index.py config.json```

The config.json should look like:

```
{
    "name": "stripe",
    "allowed_domains": ["stripe.com"],
    "start_urls": [
        "https://stripe.com/docs/"
    ]
}
```

## Docker

You might want a script like this to build and run the docker container

```
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
    -t algolia/documentation-scrapper /run
```