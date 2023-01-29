cd mini_githubcic
# uncomment this to use sqlite as test db
#export UKS_TEST_DB=ON
# collect static files and put inside ./static/
python3 manage.py collectstatic --noinput
# setup db
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py fill_database
# run Django develop server
#python3 manage.py runserver 0.0.0.0:8000
# run Django app inside gunicorn
# always use more than 1 worker
gunicorn --workers=3 mini_githubcic.wsgi -b 0.0.0.0:8000