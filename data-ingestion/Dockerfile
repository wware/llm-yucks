FROM python:3.9-slim

WORKDIR /app

RUN pip install -U pymilvus sentence-transformers

COPY . .

ENTRYPOINT ["python", "ingest.py"]
