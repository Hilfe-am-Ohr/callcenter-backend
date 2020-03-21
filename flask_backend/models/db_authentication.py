from flask_backend import db


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(db.Integer)  # Referencing DBAccount

    key = db.Column(db.String)

    def __repr__(self):
        return f"APIKey(account_id: {self.account_id}, key: {self.key})"

