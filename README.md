### Hexlet tests and linter status:
[![Actions Status](https://github.com/Nurlan-Aliev/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Nurlan-Aliev/python-project-83/actions)
[![test_lint](https://github.com/Nurlan-Aliev/python-project-83/actions/workflows/check_test.yml/badge.svg)](https://github.com/Nurlan-Aliev/python-project-83/actions/workflows/check_test.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/f1514b3a8b94fcde8711/maintainability)](https://codeclimate.com/github/Nurlan-Aliev/python-project-83/maintainability)

# [Page Analyzer]()

## About
Page analyzer is a simple web-application to get web-site base SEO characteristics.

## How to run
1. Clone this repository
   ```bash
   git clone https://github.com/Nurlan-Aliev/python-project-83.git
   ```

2. Install dependencies by poetry install
   ```bash
   poetry install
   ```

3. Create an env file with the following content
   ```txt
   DATABASE_URL = postgresql://your_name:password@localhost:PORT/your_db
    
   SECRET_KEY = your_super_strong_and_cool_secret_key
   ```
4. Run this command to create tables in your DB
   ```bash
   psql your_db < database.sql
   ```
5. Run one of commands make dev or make start
   ```bash
   make dev
   ```
   ```bash
   make start
   ```

## Build with:

* Python
* Flask
* Bootstrap
* Jinja2
* Beautiful Soup
* Requests
* Pytest
* PostgreSQL
* Flake8