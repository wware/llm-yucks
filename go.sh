#!/bin/bash -xe

ENV_VARS=
for line in $(cat $HOME/.config/api_keys.txt | grep -E '[A-Z]' | grep -v '^#')
do
    ENV_VARS=$(echo "${ENV_VARS} -e $line")
done

for x in $(docker ps -a | grep jupyter | cut -c -9)
do
    docker rm -f $x
done
docker build -t jupyter .
docker run --rm -d \
    -v "$(pwd):/work" \
    $ENV_VARS \
    -p 8888:8888 \
    jupyter
