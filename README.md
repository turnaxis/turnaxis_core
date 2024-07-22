Setup

- Clone the project

- switch to develop branch

- Create a virtual environment

- For those who prefer venv:

```
python3 -m venv .venv
```

activate 

```
source .venv/bin/activate
```

Create an env with the following keys

```
BEMSERVER_CORE_SETTINGS_FILE='bemserver-core-settings.py'

SQLALCHEMY_DATABASE_URI=<postgresql+psycopg://username:password@localhost/mydatabase>
BEMSERVER_CELERY_SETTINGS_FILE='bemserver-celery-settings.py'

MAIL_SERVER = <>
MAIL_PORT = <>
MAIL_USERNAME = <>
MAIL_PASSWORD = <>
MAIL_SENDER = <>
```

make sure you have an existing database for the connection you have provided

load submodule for bemserver core

```
git submodule update --init --recursive
```


apply db migrations

```
alembic -c bemserver_core/alembic.ini upgrade head

```

create user

```
 utils/bemserver_create_user --name <> --email <> --password <>
```

run the flask app

```
flask run 
```


Customizing 
making new migrations
```

alembic -c bemserver_core/alembic.ini revision --autogenerate -m "<>"
```