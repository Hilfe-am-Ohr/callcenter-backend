from flask_restful import Resource
from flask_backend.models.db_account import DBAccount
from flask_backend.models.db_call import DBCall
from flask_backend.routes import get_params_dict

from flask import request

from flask_backend.resources import api_authentication
from flask_backend import db

from flask_backend.resources import hub_communication

from datetime import datetime


class RESTCall(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all calls for a specific account
        params_dict = get_params_dict(request)

        if api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"], new_api_key=False)["status"] == "ok":
            account = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first()
        else:
            return {"status": "invalid request"}

        if account is None:
            return {"status": "invalid request"}
        else:
            return hub_communication.get_all_calls(account)

    def post(self):
        # CALLBACK URL FOR HUB SERVICE (Create a new call)
        params_dict = get_params_dict(request)

        if "phone_number" in params_dict and "account_id" in params_dict:
            phone_number = params_dict["phone_number"]
            account_id = params_dict["account_id"]

            account = DBAccount.query.filter(DBAccount.id == account_id).first()

            if account is None:
                return {"status": "account_id invalid"}

            call = DBCall()

            call.phone_number = phone_number
            call.account_id = account_id
            call.status = "pending"
            call.timestamp = datetime.now()

            db.session.add(call)
            db.session.commit()

            return {"status": "ok"}

        else:
            return {"status": "phone_number/account_id missing"}

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

            if "action" in params_dict:
                # "action" = "decline", "accept", "fulfill"

                action = params_dict["action"]

                if action in ["go_online", "go_offline", "accept"]:
                    if action == "go_online":
                        hub_communication.go_online(account)
                    elif action == "go_offline":
                        hub_communication.go_offline(account)
                    elif action == "accept":
                        if hub_communication.accept_call(account):
                            return hub_communication.get_all_calls(account)
                        else:
                            return {"status": "no new calls"}

                elif action in ["decline", "fulfill"] and "call_id" in params_dict:
                    call_id = params_dict["call_id"]
                    call = DBCall.query.filter(DBCall.id == call_id).first()

                    if call is None:
                        return {"status": "call_id invalid"}
                    else:
                        if action == "decline":
                            hub_communication.decline_call(call)
                        elif action == "fulfill":
                            hub_communication.fulfill_call(call)
                else:
                    return {"status": "action invalid/call_id missing"}

                return hub_communication.get_all_calls(account)

            else:
                return {"status": "action/call_id missing"}
