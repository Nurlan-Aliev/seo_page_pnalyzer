FROM python:3

RUN pip install poetry

COPY . /page_analyzer

WORKDIR /page_analyzer

RUN poetry config virtualenvs.create false

COPY database.sql ./page_analyzer

RUN poetry install

RUN ./build.sh
