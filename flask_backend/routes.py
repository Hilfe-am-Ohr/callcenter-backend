from flask_backend import app
from flask import render_template, request, redirect
from flask_backend.resources import api_authentication
import time

from flask_backend.resources.email_verification import confirm_email, trigger_email_verification
from flask_backend.models.db_account import DBAccount


def get_params_dict(request):

    try:
        params_dict = request.get_json(force=True)
    except:
        params_dict = {}

    if not isinstance(params_dict, dict):
        params_dict = {}

    params_dict.update(dict(request.form))
    params_dict.update(dict(request.files))

    if "email" not in params_dict:
        params_dict["email"] = None

    if "api_key" not in params_dict:
        params_dict["api_key"] = None

    if "password" not in params_dict:
        params_dict["password"] = None

    params_dict["method"] = request.method

    query_string_list = request.query_string.decode().split("&")

    for query_string_element in query_string_list:

        element_list = query_string_element.split("=")

        if len(element_list) != 2:
            continue

        element_list[0] = element_list[0].strip()
        element_list[1] = element_list[1].strip()
        if len(element_list[0]) == 0 or len(element_list[1]) == 0:
            continue

        if "," in element_list[1]:
            element_list[1] = list(filter(lambda x: len(x) != 0, element_list[1].split(",")))

        params_dict[element_list[0]] = element_list[1]

    print("\n\n")
    # time.sleep(0.00001)
    print(params_dict)
    return params_dict


@app.errorhandler(404)
def page_not_found(e):
    # Every url not associated with the backend is directly
    # routed to the frontend (which will also handle 404's)

    return render_template("index.html")


@app.route("/robots.txt", methods=["GET"])
def robots():
    return render_template("robots.txt")


@app.route("/backend", methods=["GET"])
def index():
    return "<h1>Welcome to Flask!</h1>"


@app.route("/backend/login", methods=["POST"])
def backend_login():
    params_dict = get_params_dict(request)

    email = params_dict["email"]
    password = params_dict["password"]
    api_key = params_dict["api_key"]

    # Initial login
    if email is not None and password is not None:
        # Artificial delay to further prevent brute forcing
        time.sleep(0.05)

        login_result_dict = api_authentication.login_account(params_dict["email"], params_dict["password"])
        return login_result_dict, 200

    # App tries to automatically re-login client
    if email is not None and api_key is not None:
        # TODO: Generate new API Key for every login request in production!
        login_result_dict = api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"])
        return login_result_dict, 200
    else:
        return {"status": "missing parameter email/password/api_key"}, 200


@app.route("/backend/logout", methods=["POST"])
def backend_logout():
    params_dict = get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return {"Status": "missing parameter email/api_key"}, 200
    else:
        api_authentication.logout_account(params_dict["email"], params_dict["api_key"])
    return {"status": "ok"}, 200



# Actually flask-cors should take care of this but somehow it doesn't always...
@app.after_request
def apply_caching(response):
    # response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route("/backend/email/verify/<verification_token>", methods=["GET"])
def backend_verify_email(verification_token):
    if confirm_email(verification_token):
        return redirect("/account")
    else:
        return redirect("/register")


@app.route("/backend/email/resend", methods=["POST"])
def backend_verify_email():
    params_dict = get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return {"status": "missing parameter email/api_key"}, 200
    else:
        if api_authentication.is_authenticated(params_dict["email"], params_dict["api_key"])["status"] == "ok":
            account = DBAccount.query.filter(DBAccount.email == params_dict["email"]).first()
            if not account.email_verified:
                trigger_email_verification(account)
                return {"status": "ok"}, 200
            else:
                return {"status": "email already verified"}, 200
        else:
            return {"status": "email/api_key invalid"}, 200

