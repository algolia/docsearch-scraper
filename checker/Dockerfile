FROM node:4

RUN apt-get update -y && apt-get install -y jq

WORKDIR /root
RUN cd /root && mkdir checker
COPY checker/index.js /root/checker
COPY checker/package.json /root/checker
COPY checker/run /root
RUN chmod +x /root/run
RUN cd /root/checker && npm install

CMD ["/root/run"]