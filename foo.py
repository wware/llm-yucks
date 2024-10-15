"""
Experiments with LLMs using Ollama API, see
https://github.com/ollama/ollama/blob/main/docs/api.md
This is a workaround for LangChain, which seems to be
inconsistent sometimes, and poorly documented other times.
"""

import logging
import json
import os
import sys
import requests
import textwrap
from groq import Groq
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

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


#client = Groq(
#    api_key=os.environ.get("GROQ_API_KEY"),
#)
#
#chat_completion = client.chat.completions.create(
#    messages=[
#        {
#            "role": "user",
#            "content": "Explain the importance of fast language models",
#        }
#    ],
#    model="llama3-8b-8192",
#)

#print(chat_completion.choices[0].message.content)
#sys.exit(0)

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
response = chain.invoke(
    {
        "input_language": "English",
        #"output_language": "German",
        "output_language": "Mandarin",
        "input": "I love programming.",
    }
)
print(textwrap.fill(response.content, 60))
sys.exit(0)

######

PLACEHOLDER = object()

class LLM:
    def __init__(self, model):
        self.ollama_host = os.environ.get(
            "OLLAMA_HOST",
             "http://localhost:11434"
        )
        self.model = model

    def post(self, url, **data):
        """Do a HTTP POST to the Ollama server
        Returns:
            Response: whatever is returned by the POST op
        """
        logger.info(self.ollama_host + url)
        # logger.info(data)
        return requests.post(
            self.ollama_host + url,
            stream=True,
            timeout=20*60,
            json=data
        )

    def chat(self, _prompt=None, messages=None):
        assert _prompt is None, "handle this case later"
        assert isinstance(messages, list), messages

        def run_thru(msgs):
            response = self.post(
                url="/api/chat",
                model=self.model,
                # messages=mgrp
                messages=msgs
            )
            answer = self.print_streamed_response(
                response,
                lambda response: response["message"]["content"]
            )
            return answer

        messages = messages[:]
        while PLACEHOLDER in messages:
            n = messages.index(PLACEHOLDER)
            answer = run_thru(messages[:n])
            messages[n] = {"role": "assistant",
                           "content": answer}
        run_thru(messages)

    def print_streamed_response(self, response, selector):
        assert callable(selector), selector
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if "error" in json_response:
                    logger.warning(line)
                    logger.warning(json_response)
                    break
                if json_response.get('done', False):
                    break
                full_response += selector(json_response)
        logger.info(full_response)
        return full_response

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
# model_name = "mistral"
# model_name = "llama3"
model_name = "qwen2.5-coder"
# model_name = "codellama"
llm = LLM(model_name)


def code_snippet(pathname, start, finish):
    with open(pathname, encoding='utf-8') as f:
        lines = f.readlines()
        return "\n".join(lines[start-1:finish])


# Here is some code that is missing docstrings and pytest cases.
Z = """
def is_truthy(s: str):
    try:
        return int(s) != 0
    except ValueError:
        return s.lower() in ("true", "yes", "1")


def fetch_env_var(key, default=""):
    key = key.upper().replace(" ", "_").replace("-", "_")
    return os.environ.get(key, default)


def set_env_var(key, value):
    key = key.upper().replace(" ", "_").replace("-", "_")
    os.environ[key] = str(value)


def boolean_env_var(key):
    return is_truthy(fetch_env_var(key, ""))
"""

print(Z)

messages = [
    {
        "role": "system",
        "content": """
        If a prompt is Python code, then write google-style docstrings
        for all classes, methods and functions that need them.
        Otherwise, use all python code encountered so far as context to answer any
        questions.
        """
    },
    {
        "role": "user",
        "content": Z
    },
    PLACEHOLDER,
    {
        "role": "user",
        "content": """Please write some pytest cases for these functions. Test
        cases should be able to run in any order without affecting whether or
        not they pass. Avoid any use of global state. In particular, consider
        using some mocking or patching scheme for set_env_var() to avoid
        directly modifying the os.environ dictionary."""
    },
    PLACEHOLDER,
    {
        "role": "user",
        "content": """Show how these functions could be used to enable debug-level
        logging when an environment variable `DEBUG` is set to a truthy value."""
    }
]

llm.chat(messages=messages)
