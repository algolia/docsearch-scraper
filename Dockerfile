FROM python:2.7
MAINTAINER Algolia <documentationsearch@algolia.com>

RUN adduser --disabled-password --gecos docsearch docsearch

RUN pip install scrapy
RUN pip install algoliasearch

COPY docker/run /root/
RUN chmod +x /root/run

COPY src /root/src

WORKDIR /root
ENTRYPOINT ["/root/run"]
CMD []
