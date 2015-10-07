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