#!/bin/bash

while ! nc -z $MYSQL_HOST 3306;
do
    echo sleeping;
    sleep 1;
done;

echo Connected!;

python3 -u /backend/manage.py dockerrun
