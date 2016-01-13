FROM ubuntu:14.04
MAINTAINER Algolia <documentationsearch@algolia.com>

# Install DocSearch dependencies
RUN apt-get update -y
RUN apt-get install -y python-pip
RUN apt-get install -y python-dev
RUN apt-get install -y python-lxml
RUN apt-get install -y libffi-dev
RUN apt-get install -y libssl-dev
RUN pip install scrapy
RUN pip install scrapyjs
RUN pip install algoliasearch

# Put everything in /root
WORKDIR /root

# Install and configure Splash
RUN apt-get install -y git
RUN git clone https://github.com/scrapinghub/splash
RUN ./splash/dockerfiles/splash/provision.sh \
    prepare_install                          \
    install_msfonts                          \
    install_builddeps                        \
    install_deps                             \
    install_extra_fonts                      \
    install_pyqt5                            \
    install_python_deps
RUN pip3 install -e ./splash/

# Copy DocSearch files
COPY docker/run /root/
COPY src /root/src
RUN chmod +x /root/run

# Create volumes for Splash
VOLUME [                          \
    "/etc/splash/proxy-profiles", \
    "/etc/splash/js-profiles",    \
    "/etc/splash/filters",        \
    "/etc/splash/lua_modules"     \
]

ENTRYPOINT ["/root/run"]
