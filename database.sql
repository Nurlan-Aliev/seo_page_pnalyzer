DROP TABLE IF EXISTS urls, url_checks;

CREATE TABLE urls (
id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
name VARCHAR(255) UNIQUE,
created_at DATE);


CREATE TABLE url_checks (
id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
url_id INTEGER,
status_code INTEGER,
h1 VARCHAR(255),
title VARCHAR(255),
description TEXT,
created_at DATE);