Hello you,

## Getting started

### Setting up the Python environment

[pipenv][1] is used to manage the whole Python environment.

- [Install pipenv][2] (this must be done only once)
- Run `pipenv install` to create a Python virtual environment if unexisting,
  and install the Scraper's dependencies (this will have to be done each time
  dependencies are modified)
- Run `pipenv shell` to enter the Python virtual environment (this will have
  to be done each time you get back to work on the Scraper)

### Installing Chrome Headless

Websites that need JavaScript for rendering are passed through ChromeDriver.
[Download the version][4] suited to your OS and then update the
`CHROMEDRIVER_PATH` in your `.env` file.

You should be ready to go.

### Running

See the dedicated page on [Algolia's documentation web site](https://community.algolia.com/docsearch/run-your-own.html).

## Run the tests

To run the full test suite, run `./docsearch test`.

# Special instructions for Algolia employees

## Ready to deploy

If you are Algolia employee and want to manage a DocSearch account, you'll need
to copy and paste [the required variables][3] in your `.env` file.

Ping the @DocSearch team to get access to those credentials.

Clone the configurations repository in your docsearch-scraper directory. Command
to run from the scraper root:

```bash
git clone git@github.com:algolia/docsearch-configs.git configs/public
```

The CLI will then have more commands for you to run.

## Reason of a fail from the docker image

To spot why a crawl fail without watching the logs, we have defined some custom 
exit status:

| Exit code | Reason                                         |
|:---------:|------------------------------------------------|
|     3     | No record extracted from the crawl             |
|     4     | Too much hits returned from the crawl          |
|     5     | The configuration provided is not a valid JSON |


[1]: https://github.com/pypa/pipenv
[2]: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv
[3]: ./.env.example
[4]: http://chromedriver.chromium.org/downloads
