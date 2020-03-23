from flask_backend import db
from flask_backend.models.db_verification import DBEmailVerification
from flask_backend.models.db_account import DBAccount

if __name__ == "__main__":
    print(DBEmailVerification.query.all())
    print(DBAccount.query.all())
    print([account.online for account in DBAccount.query.all()])
