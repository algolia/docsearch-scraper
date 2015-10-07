FROM python:2.7

RUN pip install scrapy
RUN pip install algoliasearch

ADD configs /root/configs
ADD src /root/src

COPY docker/run /root/
RUN chmod +x /root/run

WORKDIR /root