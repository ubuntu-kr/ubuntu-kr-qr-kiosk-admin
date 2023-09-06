#!/bin/sh

python manage.py migrate
# and add this at the end
exec "$@"