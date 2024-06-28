Migrations

Initialize migrations

```
alembic init migrations

```
This will create a migrations folder in your app

running migrations

```

alembic revision --autogenerate -m "message"
```

apply migrations

```
alembic upgrade head

```

**NB -migrations already done  - dp db alembic upgrade head to apply**

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
```

make sure you have an existing database for the connection you have provided


apply db migrations

```
alembic upgrade head
```

run the flask app

```
flask run 
```