dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

link:
	poetry run flake8

install:
	poetry install

pytest:
	psql test_page_analizer < database.sql
	poetry run pytest

build:
	./build.sh

test_cov:
	psql test_page_analizer < database.sql
	poetry run pytest --cov