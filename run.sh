export PROJECT_DIR=$PWD
export DJANGO_SETTINGS_MODULE=finlogger.settings
python manage.py makemigrations
python manage.py migrate
uwsgi  --ini $INI_FILE & celery -A finlogger worker -B -l INFO