#!/bin/bash
API_KEY="$(cat api-key.txt)"
docker run -it --rm --env GROQ_API_KEY="$API_KEY" -v "$(pwd):/work:rw" lnw-app
