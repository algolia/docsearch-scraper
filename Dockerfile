FROM algolia/base-documentation-scrapper
MAINTAINER Algolia <documentationsearch@algolia.com>

# Copy DocSearch files
COPY docker/run /root/
COPY docker/check_js_render.py /root/
COPY src /root/src
RUN chmod +x /root/run

ENTRYPOINT ["/root/run"]
