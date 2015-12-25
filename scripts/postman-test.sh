#!/usr/bin/env bash
cd "$(dirname "$BASH_SOURCE")"/..
repo_root=$(pwd)

api_key="645c8a65f8c5abbedcf63f2d0b53966f"
app_id="BH4D9OD16A"
name="postman"
prefix="tim_"
config=$(cat "${repo_root}/configs/${name}.json")
mount_path="${repo_root}/src"

docker stop $name 2>/dev/null
docker rm $name 2>/dev/null

docker run \
    -e APPLICATION_ID=$app_id \
    -e API_KEY=$api_key \
    -e INDEX_PREFIX=$prefix \
    -e CONFIG="$config" \
    -v "${mount_path}:/root/src" \
    --name $name \
    -t algolia/documentation-scrapper-dev \
    /root/test

