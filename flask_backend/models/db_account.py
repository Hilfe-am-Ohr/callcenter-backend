from flask_backend import db


class DBAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)

    # Email and phone confirmation using twilio
    email = db.Column(db.String)
    email_confirmed = db.Column(db.Boolean)
    phone = db.Column(db.String)
    phone_confirmed = db.Column(db.Boolean)

    # Hashed with bcrypt
    password = db.Column(db.String)

    street = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)

    # Evaluated in the backend by using then Google Geocode API
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __repr__(self):
        return f"DBAccount(id: {self.id}, email: {self.email}, lat/lng: {self.lat}/{self.lng})"

