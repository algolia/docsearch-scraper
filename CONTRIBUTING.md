Hello you,

## Install and use the scrapper without Docker

We do recommend [pipenv][1] to install the whole python environment

- [Install pipenv][2]
- `pipenv install`
- `pipenv shell`

You should be ready to go.

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

[1]: https://github.com/pypa/pipenv
[2]: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv
[3]: ./.env.example
