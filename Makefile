test:
	poetry run pytest
	

run:
	poetry run python manage.py runserver

wsgi_run:
	poetry run gunicorn finance_majordomo.wsgi:application --bind 0.0.0.0:8000