# Jupyter notebook server from Py3 worker

```shell
(
    docker build -t jupyter . && \
        docker run --rm -d -v "$(pwd):/work" -p 8888:8888 jupyter
    # docker run --rm -it -v "$(pwd):/work" -p 8888:8888 jupyter
)
```

