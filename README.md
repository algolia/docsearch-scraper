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

## Test the UX/UI with the playground

To test it live, you can use the following HTML page:

```sh
# edit your credentials + index name in ./html/playground.html
$ open ./html/playground.html
```

## Docker

### Development

You can build a development version of the image, to be used in development. It
will build the exact same image than the prod one but will expect the
`/root/src` folder to be mapped to a volume on the host. This lets you edit the
python files in your favorite editor in the host while still being able to run
the script in a Docker environment.

First, build the development image:

```sh
docker build -t algolia/documentation-scrapper-dev -f Dockerfile.dev .
```

Then, use a script to remove any dev container and rebuild it.

```sh
$ docker stop docname
$ docker rm docname
$ docker run \
    -e APPLICATION_ID=appId \
    -e API_KEY=apiKey \
    -e INDEX_PREFIX=prefix_ \
    -e CONFIG="$(cat configs/docname.json)" \
    -v `pwd`/src:/root/src \
    --name docname \
    -t algolia/documentation-scrapper-dev \
    /root/run
```

And use this one to run the tests:

```sh
$ docker stop docname
$ docker rm docname
$ docker run \
    -e APPLICATION_ID=appId \
    -e API_KEY=apiKey \
    -e INDEX_PREFIX=prefix_ \
    -e CONFIG="$(cat configs/docname.json)" \
    -v `pwd`/src:/root/src \
    --name docname \
    -t algolia/documentation-scrapper-dev \
    /root/test

```

### Prod

In production, you build the image from the default Docker file, then run the
container.

```
$ docker build -t algolia/documentation-scrapper-dev .
$ docker run \
    -e APPLICATION_ID=appId \
    -e API_KEY=apiKey \
    -e INDEX_PREFIX=prefix_ \
    -e CONFIG="$(cat configs/docname.json)" \
    --name docname \
    -t algolia/documentation-scrapper
```
