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
        urwid \
        requests \
        python-dateutil

CMD ["/bin/bash"]
