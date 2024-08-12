FROM python:3.8@sha256:f9af3c8c4614d955495d23a665760abe3b37d4310bf9c33ea1ebf9f18991d8fe

RUN apt-get -y update 
RUN apt-get -y install python3-pip

COPY src/ /base/src/
COPY pyproject.toml README.md requirements.txt setup.py /base/

# pip install the utils library in the container
WORKDIR /base/
RUN pip3 install -e .