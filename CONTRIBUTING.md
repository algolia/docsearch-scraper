Hello you,


## Install the scrapper without Docker

We do recommend the use of [pipenv][1] to install the whole python environment

- [Install pipenv][2]
- `pipenv --python 2.7 install`

You should be ready to go.


## Run the tests

To run the full test suite, run `./docsearch test`. Note that it requires that
you have a Docker image built already.

## Special instructions for Algolia employees

If you are Algolia employee and want to manage a DocSearch account,
you'll need to add the following variables in your `.env` file:

```
APPLICATION_ID=
API_KEY=
APPLICATION_ID_PROD=
API_KEY_PROD=
HELP_SCOUT_API_KEY=
NB_HITS_MAX=

WEBSITE_USERNAME=
WEBSITE_PASSWORD=
SLACK_HOOK=
SCHEDULER_USERNAME=
SCHEDULER_PASSWORD=
MONITORING_API_KEY=
PUBLIC_CONFIG_FOLDER=<path to your docsearch-scrapy directory> + /configs/public
PRIVATE_CONFIG_FOLDER=

BASE_INTERNAL_ENDPOINT=
INTERNAL_API_AUTH=

DEPLOY_KEY=
```

Ping the @docsearch team to get access to those credentials.

## Ready to deploy
Clone the configurations repo in your docsearch-scraper directory. Command to run from the scraper root:
```bash
git clone git@github.com:algolia/docsearch-configs.git configs/public
```
The CLI will then have more commands for you to run. 

[1]: https://github.com/pypa/pipenv
[2]: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv

