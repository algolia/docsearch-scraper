FROM algolia/base-documentation-scrapper
MAINTAINER Algolia <documentationsearch@algolia.com>
ARG USE_PYTHON3=false

# Install correct python version and dependencies
RUN sh /root/setup_python.sh $USE_PYTHON3

# Copy DocSearch files
COPY scraper/dev/docker/bin/run /root/
COPY scraper/dev/docker/bin/check_js_render.py /root/
COPY scraper/src /root/src
RUN chmod +x /root/run

ENTRYPOINT ["/root/run"]
