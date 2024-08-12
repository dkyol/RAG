#!/bin/bash
echo Bringing containerized services down...
docker-compose down > /dev/null 2>&1
echo Services down.
cp dump.rdb dump/dump.rdb
echo Bringing containerized services back up...
docker-compose up -d > /dev/null 2>&1
echo Services back up.
