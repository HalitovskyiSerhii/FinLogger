export PROJECT_DIR=$PWD
export DJANGO_SETTINGS_MODULE=finlogger.settings
uwsgi --http :9090 --chdir $PROJECT_DIR --module finlogger.wsgi:application & celery -A finlogger worker -B -l INFO