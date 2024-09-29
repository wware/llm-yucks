import os
import weaviate
from sentence_transformers import SentenceTransformer

# Initialize Weaviate client
client = weaviate.Client("http://localhost:8080")
# client = weaviate.Client("http://weaviate:8080")

# Check if the 'PythonSource' class already exists, and create it if it doesn't
if not 'PythonSource' in [class_name['class'] for class_name in client.schema.get()['classes']]:
    # Define Weaviate schema for storing Python source code and vectors
    schema = {
        "classes": [
            {
                "class": "PythonSource",
                "description": "A class representing Python source code files along with their vector embeddings",
                "properties": [
                    {
                        "name": "filename",
                        "dataType": ["string"],
                        "description": "The name of the source code file"
                    },
                    {
                        "name": "code",
                        "dataType": ["text"],
                        "description": "The content of the source code file"
                    },
                    {
                        "name": "vector",
                        "dataType": ["number[]"],
                        "description": "Vector embedding of the source code"
                    }
                ]
            }
        ]
    }
    client.schema.create(schema)

# Load the Sentence Transformer model for generating vectors
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_and_store(filepath):
    with open(filepath, 'r') as file:
        code = file.read()
    
    # Generate a vector embedding
    vector = model.encode(code).tolist()

    # Metadata for the file
    filename = os.path.basename(filepath)
    
    # Create a data object to store in Weaviate
    data_object = {
        "filename": filename,
        "code": code,
        "vector": vector
    }

    # Store the data object in Weaviate
    client.data_object.create(
        data_object=data_object,
        class_name="PythonSource"
    )

if __name__ == "__main__":
    # Define the directory containing the Python source files
    source_dir = '/path/to/source/code'

    # Iterate over all Python files in the specified directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                embed_and_store(os.path.join(root, file))
