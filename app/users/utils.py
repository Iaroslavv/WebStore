from flask_mail import Message
from app import mail
from flask import current_app, url_for


def send_reset_email(user):
    token = user.get_reset_token()
    body = f'''To reset your password, visit the following link:
{url_for("reset_token", token=token, _external=True)}
If you did not make this request then simply ignore this email.
'''
    msg = Message(
        "Password reset request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user.email],
        body=body,
        )
    mail.send(msg)
