FROM prospero_base:latest

# pip install the other python requirements in the container
COPY requirements.txt /web/requirements.txt
WORKDIR /web/
RUN pip3 install -r requirements.txt

# copy the src code into the directory in the container
COPY src/ /web/src/

WORKDIR /web/src/

COPY tokenizer.model /web/src/tokenizer.model

CMD gunicorn --worker-class gevent \
  --workers 3 \
  --bind 0.0.0.0:5000 \
  app:app
