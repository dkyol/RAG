FROM prospero_base:latest

# pip install the other python requirements in the container
COPY requirements.txt /judge/requirements.txt
WORKDIR /judge/
RUN pip3 install -r requirements.txt

# copy the judge src code into the /judge/ directory in the container
COPY src/ /judge/src/
WORKDIR /judge/src/