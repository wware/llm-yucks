#!/bin/bash -xe
docker rm -f ollama || true
# docker run -d -v $HOME/.ollama:/root/.ollama -v docs:/mnt/data/mistral -p 11434:11434 --name ollama ollama/ollama ollama serve
docker run -d -v $HOME/.ollama:/root/.ollama -v docs:/mnt/data/mistral -p 11434:11434 --name ollama ollama/ollama serve
