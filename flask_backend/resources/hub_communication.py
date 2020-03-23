
from flask_backend import db
from flask_backend.models.db_call import DBCall


def get_all_calls(account):
    pending_calls = DBCall.query.filter(DBCall.account_id == account.id).filter(
        DBCall.status == "pending").all()
    accepted_calls = DBCall.query.filter(DBCall.account_id == account.id).filter(
        DBCall.status == "accepted").all()
    fulfilled_calls = DBCall.query.filter(DBCall.account_id == account.id).filter(
        DBCall.status == "fulfilled").all()

    pending_calls_dict = [{
        "id": call.id,
        "timestamp": call.timestamp.strftime("%d.%m.%Y, %H:%M:%S"),
        "status": call.status
    } for call in pending_calls]

    accepted_calls_dict = [{
        "id": call.id,
        "phone_number": call.phone_number,
        "timestamp": call.timestamp.strftime("%d.%m.%Y, %H:%M:%S"),
        "status": call.status
    } for call in accepted_calls]

    fulfilled_calls_dict = [{
        "id": call.id,
        "phone_number": call.phone_number,
        "timestamp": call.timestamp.strftime("%d.%m.%Y, %H:%M:%S"),
        "status": call.status
    } for call in fulfilled_calls]

    result = {
        "status": "ok",
        "account": {
            "online": account.online,
            "email": account.email,
            "email_verified": account.email_verified,
            "address": {
                "zip": account.zip,
                "city": account.city,
                "country": account.country,
            },
            "coordinates": {
                "lat": account.lat,
                "lng": account.lng,
            }
        },
        "calls": {
            "accepted": accepted_calls_dict,
            "fulfilled": fulfilled_calls_dict
        }
    }

    return result


def go_online(account):
    # TODO: POST online notice to hub
    account.online = True
    db.session.commit()


def go_offline(account):
    # TODO: POST Decline of all pending posts
    DBCall.query.filter(DBCall.account_id == account.id).filter(DBCall.status == "pending").delete()
    # TODO: POST offline notice to hub
    account.online = False
    db.session.commit()


def accept_call(account):
    # TODO: POST accept to hub
    call = DBCall.query.filter(DBCall.status == "pending").filter(DBCall.account_id == account.id).order_by(DBCall.timestamp.asc()).first()

    if call is None:
        return False
    else:
        call.status = "accepted"
        db.session.commit()
        return True


def decline_call(call):
    # TODO: POST decline to hub
    DBCall.query.filter(DBCall.id == call.id).delete()
    db.session.commit()


def fulfill_call(call):
    # TODO: POST fulfilled to hub
    call.status = "fulfilled"
    db.session.commit()
