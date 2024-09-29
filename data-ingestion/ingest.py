from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
import os


source_dir = '/home/wware/playdir/llm-new-work'


# Connect to Milvus
connections.connect(host='milvus', port='19530')

# Create a Milvus collection (if it doesn’t exist)
collection_name = 'code_embeddings'
dim = 768
collection = Collection(name=collection_name, schema=[...], auto_id=True)

# Load Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_and_store(filepath):
    with open(filepath, 'r') as f:
        code = f.read()
    embedding = model.encode(code)
    collection.insert([[embedding]])

if __name__ == '__main__':
    # Iterate over Python source files and ingest them
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                embed_and_store(os.path.join(root, file))
