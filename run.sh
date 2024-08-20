#!/bin/bash

# Wait for db to be up
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Run migrations
python3 manage.py migrate

if [ $? -eq 0 ]; then
  echo "Migrations done, executing triggers..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -d $POSTGRES_DB -h $POSTGRES_DB -f ./setup_audit.sql

  if [ $? -eq 0 ]; then
    echo "Triggers created successfuly"
  else
    echo "Error creating the triggers"
  fi
else
  echo "Error running migrations"
fi

# Create super-user
echo "from django.contrib.auth.models import User; \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'LST@example.com', 'LST')" | python3 manage.py shell

# Start Django server
exec python3 manage.py runserver 0.0.0.0:8000