#!/bin/sh

./docsearch docker:build

docker push algolia/docsearch-scrapper-base:latest
docker push algolia/docsearch-scrapper:latest

git checkout $current_branch