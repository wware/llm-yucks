FROM python:3.9-slim

WORKDIR /app

RUN pip install -U sentence-transformers
RUN pip install weaviate-client>=3.26.7;<4.0.0

COPY . .

ENTRYPOINT ["python", "ingest.py"]
