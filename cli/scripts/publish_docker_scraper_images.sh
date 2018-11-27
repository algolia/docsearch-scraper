#!/bin/sh

./docsearch docker:build

docker push algolia/docsearch-scraper-base:latest
docker push algolia/docsearch-scraper:latest

git checkout $current_branch