#!/bin/bash

# Create network if does not exist
docker network inspect prospero >/dev/null 2>&1 || docker network create prospero 

if [[ ! -z $(curl --connect-timeout 1 -s http://169.254.169.254/1.0/) ]]; then 
    echo "Detected this is an AWS EC2 instance"
    if [[ -z "$PROSPERO_ENV" ]]; then
        echo "ERROR. Must set PROSPERO_ENV as environment variable. Acceptable values are <dev,test,prd>." 1>&2
        exit 1
    fi

    if [[ -z "$CLOUDWATCH_LOG_PREFIX" ]]; then
        CLOUDWATCH_LOG_PREFIX=prospero-$PROSPERO_ENV
        echo "Setting CLOUDWATCH_LOG_PREFIX to $CLOUDWATCH_LOG_PREFIX based on PROSPERO_ENV $PROSPERO_ENV" 
    fi
    INSTANCE_ID=$(curl --connect-timeout 1 -s http://169.254.169.254/1.0/meta-data/instance-id | xargs)

    docker run --gpus all -d -p 8000:8000 -p 8001:8001 -p 8002:8002 --name triton --network prospero \
        --restart always --shm-size=16g --ulimit memlock=-1 --ulimit stack=67108864 \
        --log-driver=awslogs --log-opt awslogs-group=$CLOUDWATCH_LOG_PREFIX-triton \
        --log-opt awslogs-stream=$INSTANCE_ID triton
else
    docker run --gpus all -d -p 8000:8000 -p 8001:8001 -p 8002:8002 --name triton --network prospero \
        --restart always --shm-size=16g --ulimit memlock=-1 --ulimit stack=67108864 triton
fi