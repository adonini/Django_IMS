#!/bin/bash

# Drops the docker
echo 'Starting the cointainers!'
docker start pgadmin_ims
docker start postgresql_ims
docker start django_ims
echo 'Done!'