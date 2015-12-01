name='stripe-test'
docker stop $name 2>/dev/null
docker rm $name 2>/dev/null

docker run \
    -e APPLICATION_ID=BH4D9OD16A \
    -e API_KEY=19724e53393cad8ccd7c95f03d37bf8c \
    -e INDEX_PREFIX= \
    -e CONFIG="$(cat configs/stripe-dev.json)" \
    -v `pwd`/src:/root/src \
    --name $name \
    -t algolia/documentation-scrapper-dev \
    /root/test
