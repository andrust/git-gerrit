FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
        curl \
        git \
        python3 \
        python3-pip \
        vim \
    && apt-get clean

RUN pip install \
        build \
        python-dateutil \
        requests \
        twine \
        urwid

CMD ["/bin/bash"]
