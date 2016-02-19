FROM node:4

WORKDIR /root
RUN cd /root && mkdir checker
COPY checker/index.js /root/checker
COPY checker/package.json /root/checker
COPY checker/run /root
RUN cd /root && mkdir configs
COPY configs /root/configs
RUN chmod +x /root/run
RUN cd /root/checker && npm install

CMD ["/root/run"]