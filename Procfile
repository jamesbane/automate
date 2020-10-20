web: gunicorn --pythonpath automate automate.wsgi
celery: cd automate && celery -A automate worker -B -l DEBUG
