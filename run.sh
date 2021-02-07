export PROJECT_DIR=$PWD
export DJANGO_SETTINGS_MODULE=finlogger.settings
python3.9 manage.py makemigrations
python3.9 manage.py migrate
uwsgi  --ini $INI_FILE & celery -A finlogger worker -B -l INFO