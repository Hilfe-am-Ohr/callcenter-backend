from flask_restful import Resource
from flask_backend.models.db_account import DBAccount
from flask_backend.models.db_authentication import APIKey
from flask_backend.routes import get_params_dict

from flask import request
import requests
import json

from flask_backend.resources import api_authentication
from flask_backend import db, bcrypt
from flask_backend import BCRYPT_SALT, GCP_API_KEY

from flask_backend.resources.email_verification import trigger_email_verification
from flask_backend.resources import hub_communication


class RESTAccount(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all infos for a specific account
        params_dict = get_params_dict(request)

        if api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"], new_api_key=False)["status"] == "ok":
            account = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first()
        else:
            return {"status": "invalid request"}

        if account is None:
            return {"status": "invalid request"}
        else:
            return {
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
                }
            }


    def post(self):
        # Create a new account
        params_dict = get_params_dict(request)

        new_account = DBAccount()

        if "account_email" in params_dict:
            if api_authentication.validate_email_format(params_dict["account_email"]):
                existing_account = DBAccount.query.filter(DBAccount.email == params_dict["account_email"]).first()
                if existing_account is not None:
                    return {"status": "email already taken"}
                else:
                    new_account.email = params_dict["account_email"]
                    new_account.email_verified = False
            else:
                return {"status": "email is invalid"}
        else:
            return {"status": "email is missing"}

        if "account_password" in params_dict:
            password = params_dict["account_password"]
            if len(password) >= 8:
                hashed_password = bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')
                new_account.password = hashed_password
            else:
                return {"status": "password is too short"}
        else:
            return {"status": "password is missing"}

        if "account_zip" in params_dict:
            # noinspection PyShadowingBuiltins
            zip = params_dict["account_zip"]
            if len(zip) == 5:
                new_account.zip = zip
            else:
                return {"status": "zip is invalid"}
        else:
            return {"status": "zip is missing"}

        if "account_city" in params_dict:
            city = params_dict["account_city"]

            if len(city) >= 2:
                new_account.city = city
            else:
                return {"status": "city is invalid"}
        else:
            return {"status": "city is missing"}

        new_account.country = "Germany"

        request_url = f"https://maps.googleapis.com/maps/api/geocode/json?" \
                      f"address={new_account.zip}+{new_account.city},{new_account.country}&" \
                      f"key={GCP_API_KEY}"

        try:
            response = requests.get(request_url)
        except:
            return {"status": "invalid google geocode request"}

        try:
            coordinates_dict = json.loads(response.text)["results"][0]["geometry"]["location"]
            new_account.lat = coordinates_dict["lat"]
            new_account.lng = coordinates_dict["lng"]
        except KeyError as e:
            db.session.expire(new_account)
            return {"status": "invalid google geocode response"}

        db.session.add(new_account)
        db.session.commit()

        # Trigger the whole verification process
        trigger_email_verification(new_account)

        # log in account and return email/api_key
        login_result_dict = api_authentication.login_account(params_dict["account_email"], params_dict["account_password"])
        return login_result_dict


    def put(self):
        # Modify an existing account
        params_dict = get_params_dict(request)



        if api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"], new_api_key=False)["status"] == "ok":
            account = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first()
        else:
            return {"status": "invalid request"}

        if account is None:
            return {"status": "invalid request"}
        else:

            if "new_email" in params_dict:
                new_email = params_dict["new_email"]

                if new_email != params_dict["email"]:

                    # Only allowed if email has not been confirmed yet
                    if not account.email_verified:

                        if api_authentication.validate_email_format(new_email):
                            existing_account = DBAccount.query.filter(DBAccount.email == new_email).first()
                            if existing_account is not None:
                                return {"status": "email already taken"}
                            else:
                                account.email = new_email
                                account.email_verified = False
                                params_dict["account_resend_email"] = True  # triggers email resend
                        else:
                            return {"status": "new email is invalid"}
                    else:
                        return {"status": "email has already been confirmed"}

            if "account_old_password" in params_dict and "account_new_password" in params_dict:
                old_password = params_dict["account_old_password"]
                new_password = params_dict["account_new_password"]
                if bcrypt.check_password_hash(account.password, old_password + BCRYPT_SALT):
                    hashed_password = bcrypt.generate_password_hash(new_password + BCRYPT_SALT).decode('UTF-8')
                    account.password = hashed_password
                    account.password = hashed_password
                else:
                    db.session.expire(account)
                    return {"status": "password invalid"}

            if "account_zip" in params_dict:
                account.zip = params_dict["account_zip"]

            if "account_city" in params_dict:
                account.city = params_dict["account_city"]

            request_url = f"https://maps.googleapis.com/maps/api/geocode/json?" \
                          f"address={account.zip}+{account.city},{account.country}&" \
                          f"key={GCP_API_KEY}"

            try:
                response = requests.get(request_url)
            except:
                return {"status": "invalid google geocode request"}

            try:
                coordinates_dict = json.loads(response.text)["results"][0]["geometry"]["location"]
                account.lat = coordinates_dict["lat"]
                account.lng = coordinates_dict["lng"]
            except KeyError as e:
                db.session.expire(account)
                return {"status": "invalid google geocode response"}

            db.session.commit()

            if "account_resend_email" in params_dict:
                trigger_email_verification(account)

            return hub_communication.get_all_calls()

    def delete(self):
        # Delete an existing account
        params_dict = get_params_dict(request)

        if api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"], new_api_key=False)["status"] == "ok":
            account = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first()
        else:
            return {"status": "invalid request"}

        if account is None:
            return {"status": "invalid request"}
        else:

            # Remove all related API Keys (logins)
            account_id = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first().id
            APIKey.query.filter(APIKey.account_id == account_id).delete()

            DBAccount.query.filter(DBAccount.email == params_dict["email"]).delete()

            db.session.commit()

            return {"status": "ok"}



