#!/bin/sh

current_branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

git checkout master || exit 1
git pull origin master

docker build -t algolia/documentation-scrapper-checker -f doctor/dev/docker/Dockerfile .
docker push algolia/documentation-scrapper-checker:latest

git checkout $current_branch