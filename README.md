# Documentation scraper

This is the repository for the DocSearch scaper. You can run it on your own, or [ask us](https://community.algolia.com/docsearch/) to crawl your documentation. 

DocSearch is in fact 3 different projects.
* The front-end of DocSearch: https://github.com/algolia/docsearch
* The scraper which browse & index web pages: https://github.com/algolia/docsearch-scraper
* The configurations for the scraper: https://github.com/algolia/docsearch-configs

This project is a collection of submodules, each one in it’s own directory:
* cli: A command line tool to manage DocSearch. Run `./docsearch` and follow the steps
* deployer: Tool used by Algolia to deploy the configuration in our mesos infrastructure
* doctor: A monitoring/repairing tool to check if the indices built by the scraper are in good shape
* playground: An HTML page to easily test DocSearch indices
* scraper: The core of the scraper. It reads the configuration file, fetch the web pages and index them in Algolia.


## Getting started

### Install Docsearch

- Install python
  - `brew install python # will install pip`
  - `apt-get install python`
  - Or every other way 
- `git clone git@github.com:algolia/documentation-scraper.git`
- `cd documentation-scraper`
- `pip install -r requirements.txt`
- Depending on what you want to do you might also need to install **docker** especially to run tests

### Set up Docsearch

Create a `.env` file at the root of the project

```
APPLICATION_ID=
API_KEY=
```

To have the APPLICATION_ID and API_KEY, you need to create an [https://www.algolia.com/users/sign_up](Algolia account)

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

### Use Docsearch

#### Create a config

To use docsearch the first thing you need is to create the config for the crawler.
For more details about configs, check out https://github.com/algolia/docsearch-configs,
you'll have a list of options you can use and a lot of live and working examples

#### Crawl the website

Without docker

```sh
$ ./docsearch run /path/to/your/config
```

With docker

```sh
$ ./docsearch docker:build-scraper #Build the docker file
$ ./docsearch config:docker-run /path/to/your/config #run the docker container
```

#### Check that everything went well

open `./playground/index.html` in your browser, enter your credentials, your index name, and do type some queries
to make sure everything is ok

#### Use docsearch frontend

Just add this snippet to your documentation:

```
<link rel="stylesheet" href="//cdn.jsdelivr.net/docsearch.js/2/docsearch.min.css" />
<script type="text/javascript" src="//cdn.jsdelivr.net/docsearch.js/2/docsearch.min.js"></script>

var search = docsearch({
  apiKey: '<API_KEY>',
  indexName: '<INDEX_NAME>',
  inputSelector: '<YOUR_INPUT_DOM_SELECTOR>',
  debug: false
});
```

And your good to go

### Admin task

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

The cli will then have more commands for you to run

For some actions like deploying you might need to use different credentials than the one in the .env file
To do this you need to override them when running the cli tool:

```
APPLICATION_ID= API_KEY= ./docsearch deploy:configs
```
