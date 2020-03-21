from flask_backend import db, bcrypt
from flask_backend.models.db_account import DBAccount
from flask_backend.models.db_authentication import APIKey
from flask_backend import BCRYPT_SALT

import random


# ---------------------------------------------------------------------------------------------------------------------
# Helper Functions

def validate_email_format(email):
    if email is None:
        return False
    else:
        l1 = email.split("@")
        if len(l1) == 2:
            l2 = l1[1].split(".")
            if len(l2) == 2:
                return True
        return False


def generate_random_key(length=32):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    # Characters 'A' through 'Z'
    possible_characters += [chr(x) for x in range(65, 91)]

    # Characters 'a' through 'z'
    possible_characters += [chr(x) for x in range(97, 123)]

    random_key = ""

    for i in range(length):
        random_key += random.choice(possible_characters)

    return random_key



# ---------------------------------------------------------------------------------------------------------------------
# Functions to be accessed from 'routes' directly

def login_account(email, password):
    if validate_email_format(email) and len(password) >= 8:
        account = DBAccount.query.filter(DBAccount.email == email).first()

        if account is not None:
            if bcrypt.check_password_hash(account.password, password + BCRYPT_SALT):
                api_key = register_client(account)
                return {"status": "ok",
                        "email": email,
                        "api_key": api_key}
            else:
                return {"status": "invalid email/password"}
        else:
            return {"status": "invalid email/password"}
    else:
        return {"status": "invalid email/password"}



def is_authenticated(email, api_key, new_api_key=False):
    if validate_email_format(email) and len(api_key) >= 8:
        account = DBAccount.query.filter(DBAccount.email == email).first()

        if account is not None:
            api_key_object = APIKey.query\
                .filter(APIKey.account_id == account.id)\
                .filter(APIKey.key == api_key).first()
        else:
            return {"status": "invalid request"}

        if api_key_object is None:
            return {"status": "invalid request"}

        if new_api_key:
            # A new api_key is generated every time the user does this
            unregister_client(account)
            new_api_key = register_client(account)
        else:
            new_api_key = api_key

        return {"status": "ok",
                "email": email,
                "api_key": new_api_key}
    else:
        return {"status": "invalid email/api key"}


def logout_account(email, api_key):
    # Why do you need both email and api_key?
    # So that someone cannot just logout random
    # emails or api_keys to randomly hit something
    # You only know both if you have regularly
    # logged in
    account = DBAccount.query.filter(DBAccount.email == email).first()

    if account is None:
        return False

    unregister_client(account)

    return True



# ---------------------------------------------------------------------------------------------------------------------
# Direct database manipulation

def register_client(account):
    # Kick out any old key where the user did not log himself out
    APIKey.query.filter(APIKey.account_id == account.id).delete()

    api_key = APIKey()
    api_key.account_id = account.id

    # Generating a new random API key
    api_key.key = generate_random_key()

    db.session.add(api_key)
    db.session.commit()
    return api_key.key


def unregister_client(account):
    # Kick out any old key
    APIKey.query.filter(APIKey.account_id == account.id).delete()
    db.session.commit()
    return True


# ---------------------------------------------------------------------------------------------------------------------
# Just small tests

if __name__ == "__main__":
    print(generate_random_key(length=16))
    print(generate_random_key())
    print(generate_random_key(length=48))
    print(generate_random_key(length=64))
