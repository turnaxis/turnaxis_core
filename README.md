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