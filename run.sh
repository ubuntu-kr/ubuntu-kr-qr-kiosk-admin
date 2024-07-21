#!/bin/sh

python manage.py migrate
echo yes | python manage.py collectstatic
# and add this at the end
exec "$@"