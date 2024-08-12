FROM prospero_base:latest

# pip install the other python requirements in the container
COPY requirements.txt /router/requirements.txt
WORKDIR /router/
RUN pip3 install -r requirements.txt

# As of 1/31 rather than use the `pip install redisvl` command,
# We need a specific version that has Pydantic 2 compatibility
# So we clone the redisvl repo and checkout that commit
# TODO: use redisvl releaese 0.0.8 when it comes out
RUN git clone https://github.com/RedisVentures/redisvl.git /redisvl/
WORKDIR /redisvl/
RUN git checkout c3e036b0b8dbe7b76cea40a25446a1a231aaffe2
RUN pip3 install -e .

# copy the router src code into the /router/ directory in the container
COPY src/ /router/src/
WORKDIR /router/src/