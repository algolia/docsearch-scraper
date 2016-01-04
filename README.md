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
    "allowed_domains": "stripe.com",
    "start_urls": [
        "https://stripe.com/docs"
    ],
    "stop_urls": [
        "https://stripe.com/docs/api"
    ],
    "selectors_exclude": [
        ".method-list",
        "aside.note"
    ],
    "selectors": {
      "lvl0": "#content header h1",
      "lvl1": "#content article h1",
      "lvl2": "#content section h3",
      "lvl3": "#content section h4",
      "lvl4": "#content section h5",
      "lvl5": "#content section h6",
      "text": "#content header p,#content section p,#content section ol"
    },
    "custom_settings": {},
    "strategy": "default",
    "strip_chars": " :;,."
}
```

## Configuration

All config json files should be saved in `./configs`. Here is a list of all
available options.

### `index_name`

**Mandatory**

Name of the Algolia index where all the data will be pushed. Will be prefixed
with the `PREFIX` environment variable.

### `start_urls`

**Mandatory**

You can pass either a string or an array of urls. The crawler will go to each
page in order, following every link it finds on the page. It will only stop if
the domain is outside of the `allowed_domains` or if the link is blacklisted in
`stop_urls`.

Note that it currently does not follow 301 redirects.

### `selectors`

**Mandatory**

This object contains all the CSS selectors that will be used to create the
record hierarchy. It contains 6 levels (`lvl0`, `lvl1`, `lvl2`, `lvl3`, `lvl4`,
`lvl5`) and `text`. You should fill at least the three first levels for better
relevance.

A default config would be to target the page `title` or `h1` as `lvl0`, the `h2`
as `lvl1` and `h3` as `lvl2`. `text` is usually any `p` of text.

### `allowed_domains`

You can pass either a string or an array of strings. This is the whitelist of
domains the crawler will scan. If a link targets a page that is not in the
whitelist, the crawler will not follow it.

Default is the domain of the first element in the `start_urls`

### `stop_urls`

This is the blacklist of urls on which the crawler should stop. If a link in
a crawled webpage targets one the elements in the `stop_urls` list, the crawler
will not follow the link.

Note that you can use regexps as well as plain urls.

Note: It is sometimes needed to add `http://www.example.com/index.html` pages to
the `stop_urls` list if you set `http://www.example.com` as a `start_urls`, to
avoid duplicated content.

### `selectors_exclude`

By default, the `selectors` search is applied page-wide. If there are some parts
of the page that you do not want to include (like a header, sidebar or footer),
you can add them to the `selectors_exclude` key.

### `custom_settings`

This object is any custom Algolia settings you would like to pass to the index
settings.

### `strategy`

Don't pay attention to this config option. We currently have only one strategy
in the source code.

### `min_indexed_level`

Lets you define the minimum level at which you want records to be indexed. For
example, with a `min_indexed_level: 1`, you will only index records that have at
least a `lvl1` field.

This is especially useful when the documentation is split into several pages,
but all pages duplicates the main title (see [this issue][1].

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
$ docker build -t algolia/documentation-scrapper .
$ docker run \
    -e APPLICATION_ID=appId \
    -e API_KEY=apiKey \
    -e INDEX_PREFIX=prefix_ \
    -e CONFIG="$(cat configs/docname.json)" \
    --name docname \
    -t algolia/documentation-scrapper
```


[1]: https://github.com/algolia/documentation-scrapper/issues/7)
