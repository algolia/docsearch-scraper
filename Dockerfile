FROM python:2.7

RUN pip install scrapy
RUN pip install algoliasearch

CMD /bin/bash