# See ./base for building `prospero_base:latest` image
FROM prospero_base:latest

# pip install the other python requirements in the container
COPY requirements.txt /chunking/requirements.txt
WORKDIR /chunking/
RUN pip3 install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

# copy the chunking src code into the /chunking/ directory in the container
COPY src/ /chunking/src/
WORKDIR /chunking/src/
