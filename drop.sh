#!/bin/bash

# Drops the docker
echo 'Droping the cointainers!'
docker-compose down
sleep 2
docker volume rm django_ims_pgdata
echo 'Done!'