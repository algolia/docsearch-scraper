Hello you,

## Run the tests

To run the full test suite, run `./docsearch test`. Note that it requires that
you have a Docker image built already.

## Special instructions for Algolia employees

If you are Algolia employee and want to manage a DocSearch account,
you'll need to add the following variables in your `.env` file:

```
WEBSITE_USERNAME=
WEBSITE_PASSWORD=
SLACK_HOOK=
SCHEDULER_USERNAME=
SCHEDULER_PASSWORD=
DEPLOY_KEY=
```

Ping the @docsearch team to get access to those credentials.

The CLI will then have more commands for you to run. 


