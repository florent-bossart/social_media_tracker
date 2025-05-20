#!/usr/bin/env bash

<<<<<<< HEAD
poetry run airflow db migrate

poetry run airflow users create -r Admin -u admin -p admin -e admin@example.com -f admin -l airflow

poetry run airflow webserver
=======
airflow db migrate

airflow users create -r Admin -u admin -p admin -e admin@example.com -f admin -l airflow

airflow webserver
>>>>>>> a1d0bee8fb0f8f41024243a6eb16e9e9547e8567
