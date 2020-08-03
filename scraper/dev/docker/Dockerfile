FROM algolia/docsearch-scraper-base
LABEL maintainer="docsearch@algolia.com"

WORKDIR /root
COPY scraper/src ./src

ENTRYPOINT ["pipenv", "run", "python", "-m", "src.index"]
