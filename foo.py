import logging
import sys
import os
import time

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

documents = SimpleDirectoryReader("sources").load_data()

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama
# Settings.llm = Ollama(model="llama3", request_timeout=360.0)
Settings.llm = Ollama(model="llama3",
                      base_url="http://ollama:11434",
                      request_timeout=600.0)

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

while True:
    queries = {f for f in os.listdir() if "query" in f}
    for query in queries:
        outfile = query.replace("query", "answer")
        if os.path.isfile(outfile):
            continue
        response = query_engine.query(
            open(query).read()
        )
        open(outfile, 'w').write(str(response))
    time.sleep(5)
