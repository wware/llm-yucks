#!/bin/bash -xe
docker rm -f ollama || true
docker run -d -v ${HOME}/.ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
