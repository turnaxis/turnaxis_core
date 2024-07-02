# from bemserver_core.celery import
from .email import mail
from flask_mail import Message
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(recipient, subject, content):
    msg = Message(
        subject=subject, sender=os.getenv("MAIL_SENDER"), recipients=[recipient]
    )

    msg.body = content

    mail.send(msg)
    return "success"
