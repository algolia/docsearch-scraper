#!/usr/bin/env bash
cd "$(dirname "$BASH_SOURCE")"
repo_root=$(pwd)

# HOW TO USE:
# Build a Docker development image:
# $ docker build -t algolia/documentation-scrapper-dev -f Dockerfile.dev .
#
# Then copy this file as `./run` at the project root (it is ignored by git) and
# change the following config. After it's done, just start `./run` to start
# scraping and indexing.
app_id=${APPLICATION_ID:-"YOUR_APP_ID"}
api_key=${API_+KEY:-"YOUR_API_KEY"}
container_name="DocSearch"
prefix=""

# NO NEED TO CHANGE ANYTHING AFTER THIS LINE
if [[ -z "$1" ]]; then
	echo "Please provide a path to a configuration as the first argument"
	echo "Usage: "
	echo "	APPLICATION_ID=\"YOUR_APP_ID\" API_KEY=\"YOUR_API_KEY\" $0 path/to/config.json"
	exit 1
fi

config=$(cat "$1")
mount_path="${repo_root}/src"

docker stop $container_name 1>/dev/null
docker rm $container_name 1>/dev/null

docker run \
    -e APPLICATION_ID=$app_id \
    -e API_KEY=$api_key \
    -e INDEX_PREFIX=$prefix \
    -e CONFIG="$config" \
    -v "${mount_path}:/root/src" \
    --name $container_name \
    -t algolia/documentation-scrapper \
    /root/run
