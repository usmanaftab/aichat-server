from flask import current_app, request
from flask_mail import Message, Mail

mail = Mail()

def send_reset_password_email(email, token):
    msg = Message(
        'Password Reset Request',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f'''To reset your password, visit the following link:
    {current_app.config['WEB_CLIENT_URL']}reset-password?token={token}

    If you did not make this request, please ignore this email.
    '''
    mail.send(msg)

def send_email(email, subject, body):
    msg = Message(
        subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = body
    mail.send(msg)