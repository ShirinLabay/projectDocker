#!/bin/bash

docker-compose up -d

sleep 10

./initmongo.sh

./ngrok-run.sh