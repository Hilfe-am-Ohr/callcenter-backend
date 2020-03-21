from flask_backend import db


class DBEmailConfirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(db.Integer)
    verification_token = db.Column(db.String)

    def __repr__(self):
        return f"DBEmailConfirmation(account_id: {self.account_id}, verification_token: {self.verification_token})"


class DBPhoneConfirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(db.Integer)
    verification_token = db.Column(db.String)

    def __repr__(self):
        return f"DBPhoneConfirmation(account_id: {self.account_id}, verification_token: {self.verification_token})"
