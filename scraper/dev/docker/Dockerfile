FROM algolia/docsearch-scraper-base
MAINTAINER Algolia <documentationsearch@algolia.com>

WORKDIR /root

ENTRYPOINT ["pipenv", "run", "python", "-m", "src.index"]
