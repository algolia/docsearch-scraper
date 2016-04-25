#!/bin/bash
cd "$(dirname "$BASH_SOURCE")"
repo_root=$(pwd)

api_key="b59b637f15d74ed060008de4da0cb056"
app_id="P8MNSEC776"
config_name="configName"
container_name="algolia-documentation-scrapper-dev"
prefix="prefix_"
# NO NEED TO CHANGE ANYTHING AFTER THIS LINE

config="$(cat "$1")"
mount_path="${repo_root}/src"

docker stop $container_name 2>/dev/null
docker rm $container_name 2>/dev/null

docker run \
    -e APPLICATION_ID=$app_id \
    -e API_KEY=$api_key \
    -e INDEX_PREFIX=$prefix \
    -e CONFIG="$config" \
    -v "${mount_path}:/root/src" \
    --name $container_name \
    -t algolia/documentation-scrapper-dev \
    /root/run
