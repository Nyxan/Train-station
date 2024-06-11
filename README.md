# Train station API

Django rest framowork project - system of managing trains, journeys, crew and stations

## Installing / Getting started

Python3 must be already installed

```shell
git clone https://github.com/Nyxan/train-station
cd train-station
python3 -m venv venv
source venv/scripts/activate
pip install -r requirements.txt
set POSTGRES_HOST=<your db hostname>
set POSTGRES_NAME=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver
```

## Run with docker

Docker should be installed

```shell
docker-compose build
docker-compose up
```

## Getting access

* create user via /api/user/register/
* get access token via /api/user/token/

## Features

* JWT Authentication
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing order and tickets on user side
* Managing trains, train types, stations on admin side
* Filtering trains

Project in develop

