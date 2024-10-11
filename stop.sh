#!/bin/bash

# Drops the docker
echo 'Stopping the cointainers!'
docker stop pgadmin_ims
docker stop postgresql_ims
docker stop django_ims
echo 'Done!'