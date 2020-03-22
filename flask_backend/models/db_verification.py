from flask_backend import db


class DBEmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(db.Integer)
    token = db.Column(db.String)

    def __repr__(self):
        return f"DBEmailVerification(account_id: {self.account_id}, token: {self.token})"

