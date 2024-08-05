"""
Experiments with LLMs using Ollama API, see
https://github.com/ollama/ollama/blob/main/docs/api.md
This is a workaround for LangChain, which seems to be
inconsistent sometimes, and poorly documented other times.
"""

import logging
import json
import os
import requests

logger = logging.getLogger()
level = logging.INFO
h = logging.StreamHandler()
h.setFormatter(logging.Formatter(
    "%(asctime)-15s  %(filename)s:%(lineno)d  %(message)s"
))
logger.setLevel(level)
h.setLevel(level)
logger.handlers = [h]
logger.info("Logger %s is set up", logger)

PLACEHOLDER = object()

class LLM:
    def __init__(self, model="tinyllama"):
        self.ollama_host = os.environ.get("OLLAMA_HOST")
        self.model = model
        # curl http://localhost:11434/api/pull -d '{
        # "name": "llama3"
        # }'
        response = self.post(url="/api/pull", model=model)
        okay = False
        for line in response.iter_lines():
            if line:
                # logger.info(line)
                json_response = json.loads(line)
                if json_response.get("status", "").lower() == "success":
                    okay = True
                    break
        assert okay

    def post(self, url, **data):
        """Do a HTTP POST to the Ollama server
        Returns:
            Response: whatever is returned by the POST op
        """
        logger.info(self.ollama_host + url)
        logger.info(data)
        return requests.post(
            self.ollama_host + url,
            stream=True,
            timeout=60,
            json=data
        )

    def chat(self, _prompt=None, messages=None):
        if _prompt is None:
            _prompt = "Why is there air?"
        if messages is None:
            messages = [{
                "role": "user",
                "content": _prompt
            }]
        logger.info("")
        message_groups = []
        while messages:
            logger.info(messages)
            if PLACEHOLDER not in messages:
                break
            n = messages.index(PLACEHOLDER)
            logger.info(n)
            this, messages = messages[:n], messages[n+1:]
            message_groups.append(this)
        logger.info("")
        if messages:
            logger.info(messages)
            message_groups.append(messages)
        logger.info(message_groups)
        for mgrp in message_groups:
            logger.info(mgrp)
            response = self.post(
                url="/api/chat",
                model=self.model,
                messages=mgrp
            )
            self.print_streamed_response(
                response,
                lambda response: response["message"]["content"]
            )

    def print_streamed_response(self, response, selector):
        assert callable(selector), selector
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                try:
                    full_response += selector(json_response)
                except:
                    logger.warning(line)
                    logger.warning(json_response)
                    raise
                if json_response['done']:
                    break
        logger.info(full_response)

    def generate(self, _prompt):
        response = self.post(
            url="/api/generate",
            model=self.model,
            prompt=_prompt
        )
        self.print_streamed_response(
            response,
            lambda response: response["response"]
        )


# model_name = "tinyllama"
model_name = "mistral"
# model_name = "llama3"
# model_name = "codellama"
llm = LLM(model_name)
# prompt = "Why is the sky blue?"
# prompt = "Why are manhole covers circular?"
# prompt = "Is the space shuttle still flying?"

# prompt = """\
# Question about Flask-SQLAlchemy. There is a method `flask_sqlalchemy.SQLAlchemy.init_app`
# where credentials are established for using a database. I have a database where a token
# is periodically updated for security reasons. I find I cannot make repeated calls
# to the `init_app` method, it should be called only once. What can I do instead?
# """

messages = [
    {
        "role": "system",
        "content": """
        If a prompt begins with "TRANSLATE", Convert the rest of the prompt from English to
        RDF Turtle language. Nouns become entities or graph vertices.
        If the prompt does not begin with "TRANSLATE" then take it as instructions and do
        what it says.
        """
    },
    {
        "role": "user",
        "content": "TRANSLATE Bob likes grilled cheese sandwiches."
    },
    {
        "role": "assistant",
        "content": """
        @prefix :       <> .
        @prefix owl:    <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
        @foaf:          <http://xmlns.com/foaf/0.1/> .
        :GrilledCheeseSandwich rdfs:subClassOf :Food .
        :Bob a :Person .
        :Bob foaf:likes :GrilledCheeseSandwich .
        """
    },
    {
        "role": "user",
        "content": "TRANSLATE Jenny likes seafood."
    },
    PLACEHOLDER,
    {
        "role": "user",
        "content": "Take the Turtle piece about Jenny and seafood and translate it to RDF/XML."
    },
]

llm.chat(messages=messages)
