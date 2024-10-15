# Fooling with LLM application stuff

Try using the Groq API to do some LLM app stuff. According to the
[docs](https://python.langchain.com/docs/integrations/chat/groq/),
Groq should be compatible with langchain.

```
API_KEY="$(cat api-key.txt)"
docker run -it --rm --env GROQ_API_KEY="$API_KEY" -v "$(pwd):/work:rw" lnw-app
```
