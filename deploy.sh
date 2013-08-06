#!/bin/bash

cd /srv/www/cgt/src
/usr/bin/git pull
/usr/bin/supervisorctl restart cgt
# source are csh-ism
. /srv/www/envs/cgt/bin/activate
python manage.py collectstatic --noinput --settings=cgt.production
