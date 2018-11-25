FROM algolia/base-docsearch-scraper
MAINTAINER Algolia <documentationsearch@algolia.com>

WORKDIR /root

ENTRYPOINT ["pipenv", "run", "python", "-m", "src.index"]
