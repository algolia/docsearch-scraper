# Documentation scraper

## Getting started

#### Install DocSearch

- Install python
  - `brew install python # will install pip`
  - `apt-get install python`
  - Or every other way 
- `pip install -r requirements.txt`
- `git clone git@github.com:algolia/documentation-scraper.git`
- `cd documentation-scraper`
- Depending on what you want to do you might also need to install **docker** especially to run tests
Create a `.env` file at the root of the project


```
APPLICATION_ID=
API_KEY=
```

If you are Algolia employee and want to manage docsearch account
your need to add the following variables in your `.env` file

```
WEBSITE_USERNAME=
WEBSITE_PASSWORD=
SLACK_HOOK=
SCHEDULER_USERNAME=
SCHEDULER_PASSWORD=
DEPLOY_KEY=
```

#### Use the project

**You should be able to do everything** with the docsearch CLI tool:

```sh
$ ./docsearch
Docsearch CLI

Usage:
  ./docsearch command [options] [arguments]

Options:
  --help    Display help message

Available commands:
  test                  Run tests
  playground            Launch the playground
  run                   Run a config
 config
  config:bootstrap      Boostrap a docsearch config
  config:docker-run     Run a config using docker
 docker
  docker:build-scraper  Build scraper images (dev, prod, test)
```