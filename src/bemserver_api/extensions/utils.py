import secrets
import string
from datetime import datetime, timedelta


digits = string.digits


def generate_random_token(length):
    return "".join(secrets.choice(digits) for _ in range(length))


def generate_expiry_date(time, unit="minutes"):
    kwargs = {unit: time}
    return datetime.now() + timedelta(**kwargs)


def get_current_date_time():
    return datetime.now()