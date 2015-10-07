docker build -t algolia/documentation-scrapper . || exit 1

docker stop documentation-scrapper > /dev/null 2>&1 || true
docker rm documentation-scrapper > /dev/null 2>&1 || true

docker run \
    -v "`pwd`":/root \
    -d \
    --name documentation-scrapper \
    -t algolia/documentation-scrapper
