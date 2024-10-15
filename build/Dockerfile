FROM python:3.11-slim

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    curl \
    wget \
    procps \
    mlocate \
    vim \
    psmisc \
    htop \
    less \
    golang \
    ripgrep && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/local/go
ENV GOPATH=/usr/local/go

# Install PyTorch with CPU-only support
# ENV TORCH_CPU_ONLY=1
# RUN wget https://download.pytorch.org/whl/cpu/torch-2.2.0%2Bcpu-cp311-cp311-linux_x86_64.whl

# RUN curl -fsSL https://ollama.com/install.sh | sh

RUN apt-get update -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.11 get-pip.py
RUN pip install -U pip
RUN pip install setuptools wheel requests
# RUN pip install torch-2.2.0+cpu-cp311-cp311-linux_x86_64.whl
RUN pip install llama-index-llms-ollama llama-index-embeddings-huggingface
RUN pip install -U llama-index

RUN apt-get update -y
# COPY . .
# RUN updatedb

WORKDIR /work
CMD ["python3.11", "foo.py"]
