#!/bin/sh

echo "启动"
mkdir -p /var/www/django/message/static/
mkdir -p /var/www/django/message/static/files
python3 manage.py collectstatic --noinput
uwsgi --ini /var/www/django/message/conf/tke/uwsgi.ini