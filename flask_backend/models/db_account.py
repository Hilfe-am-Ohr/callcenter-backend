from flask_backend import db


class DBAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Email and phone confirmation using twilio
    email = db.Column(db.String)
    email_verified = db.Column(db.Boolean)

    # Hashed with bcrypt
    password = db.Column(db.String)

    zip = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)

    # Evaluated in the backend by using then Google Geocode API
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    # If online the hub sends pending request to this person
    online = db.Column(db.Boolean)

    def __repr__(self):
        return f"DBAccount(id: {self.id}, email: {self.email}, lat/lng: {self.lat}/{self.lng})"

