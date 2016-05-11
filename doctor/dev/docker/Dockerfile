FROM node:4

RUN apt-get update -y && apt-get install -y jq

WORKDIR /root
RUN cd /root && mkdir checker
COPY doctor/src/index.js /root/checker
COPY doctor/package.json /root/checker
RUN cd /root/checker && npm install
COPY doctor/dev/docker/bin/run /root
RUN chmod +x /root/run

CMD ["/root/run"]