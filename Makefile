install:
	poetry install

test:
	poetry run pytest
	
test-coverage:
	poetry run pytest --cov=finance_majordomo --cov-report xml

run:
	poetry run python manage.py runserver

wsgi_run:
	poetry run gunicorn finance_majordomo.wsgi:application --bind 0.0.0.0:8000
	
migrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate