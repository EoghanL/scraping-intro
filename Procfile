web: PYTHONPATH=$PYTHONPATH:$PWD/project gunicorn config.wsgi --log-file -
worker: PYTHONPATH=$PYTHONPATH:$PWD/project python project/manage.py rqworker
