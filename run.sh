#!/bin/sh

if [ "$1" = "gunicorn" ]; then
    python manage.py migrate
    python manage.py collectstatic --noinput
fi

exec "$@"
