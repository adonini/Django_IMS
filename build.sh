#!/bin/bash

# Builds the docker
docker-compose up -d 

container_name="django_ims"

until [ "$(docker inspect -f '{{.State.Running}}' $container_name)" == "true" ]; do
    sleep 1
    echo "Waiting for the cointainer to start running..."
done

echo "This will take a little"
sleep 10

echo "Container is running."

docker exec -it $container_name bash -c "echo 'Container ready.'; python manage.py runscript populate_data"

echo "Commands done."