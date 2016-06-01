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

``
WEBSITE_USERNAME=
WEBSITE_PASSWORD=
SLACK_HOOK=
SCHEDULER_USERNAME=
SCHEDULER_PASSWORD=
DEPLOY_KEY=
``

#### Use the project

**You should be able to do everything** with the docsearch CLI tool:

```sh
$ ./docsearch
```

will print the usage