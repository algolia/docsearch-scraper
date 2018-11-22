FROM algolia/base-docsearch-scraper
MAINTAINER Algolia <documentationsearch@algolia.com>

WORKDIR /root

# Copy DocSearch files
COPY scraper/dev/docker/bin/run .
COPY scraper/dev/docker/bin/check_js_render.py .
COPY scraper/src ./src
RUN chmod +x ./run

ENTRYPOINT ["/root/run"]
