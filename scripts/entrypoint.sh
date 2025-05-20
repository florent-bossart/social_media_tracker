#!/usr/bin/env bash

poetry run airflow db migrate

poetry run airflow users create -r Admin -u admin -p admin -e admin@example.com -f admin -l airflow

poetry run airflow webserver
