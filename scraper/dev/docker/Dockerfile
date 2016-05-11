FROM algolia/base-documentation-scrapper
MAINTAINER Algolia <documentationsearch@algolia.com>

# Copy DocSearch files
COPY scraper/dev/docker/bin/run /root/
COPY scraper/dev/docker/bin/check_js_render.py /root/
COPY scraper/src /root/src
RUN chmod +x /root/run

ENTRYPOINT ["/root/run"]
