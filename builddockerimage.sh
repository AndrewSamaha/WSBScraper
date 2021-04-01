#!/bin/sh
docker build -f ./Dockerfile -t test/wsbscraper .
docker run --name wsbscraper -p 27017:27017 -v "$PWD":/home/andrew test/wsbscraper