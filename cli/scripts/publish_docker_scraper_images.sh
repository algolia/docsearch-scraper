#!/bin/sh

current_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

git checkout master || exit 1
git pull origin master

./docsearch docker:build

docker push algolia/docsearch-scrapper-base:latest
docker push algolia/docsearch-scrapper:latest

git checkout $current_branch