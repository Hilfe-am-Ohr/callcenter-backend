
from flask_backend import db


def reset_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    reset_db()
