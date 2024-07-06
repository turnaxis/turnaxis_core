# from bemserver_core.celery import
from ..extensions.email import mail
from flask_mail import Message
from dotenv import load_dotenv
import os
from bemserver_core.email import send_email
from bemserver_core.celery import celery


load_dotenv()


@celery.task(name="send_email")
def send_email(recipient, subject, content):
    msg = Message(
        subject=subject, sender=os.getenv("MAIL_SENDER"), recipients=[recipient]
    )

    msg.body = content

    mail.send(msg)
    return "success"
