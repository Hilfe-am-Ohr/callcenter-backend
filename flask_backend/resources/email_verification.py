from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization, Substitution

from sendgrid.helpers.mail import *
from sendgrid import *

from flask_backend import db, SENDGRID_API_KEY

from flask_backend.models.db_verification import DBEmailVerification
from flask_backend.models.db_account import DBAccount
from flask_backend.resources.api_authentication import generate_random_key

import os
import ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def send_verification_mail(email, verification_token):

    message = Mail(
        from_email='verify@hilfe-am-ohr.de',
        to_emails=email,
        subject='Verify your account!',
        html_content=f'Please verify: <a href=\'http://localhost:5000/backend/email/verify/{verification_token}\'>Verification Link</a>')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def confirm_email(verification_token):
    verification_record = DBEmailVerification.query.filter(DBEmailVerification.token == verification_token).first()

    if verification_record is not None:
        account_record = DBAccount.query.filter(DBAccount.id == verification_record.account_id).first()
        if account_record is not None:
            account_record.email_verified = True
            DBEmailVerification.query.filter(DBEmailVerification.token == verification_token).delete()
            db.session.commit()
            return True
        else:
            # Don't know how this should happen
            return False
    else:
        return False



def trigger_email_verification(account):
    # Remove all old confirmation tokens
    DBEmailVerification.query.filter(DBEmailVerification.account_id == account.id).delete()
    db.session.commit()

    # Generate new token
    verification_token = generate_random_key(length=64)

    # Create new token record
    verification_record = DBEmailVerification()
    verification_record.account_id = account.id
    verification_record.token = verification_token
    db.session.add(verification_record)
    db.session.commit()

    # Trigger token-email
    send_verification_mail(account.email, verification_token)

